"""
automation/supervisor.py
멀티 프로젝트 supervisor.

매시간 cron으로 깨워:
1. 각 프로젝트 inbox(이슈, Sentry 알림 등) 수집
2. 우선순위 큐 정렬
3. 일일 예산 안에서 상위 N개를 router.py로 디스패치

설정: ~/.claude-orchestrator/projects.yaml
"""

import asyncio
import os
import sqlite3
import subprocess
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: pip install pyyaml", file=sys.stderr)
    sys.exit(1)


CONFIG_DIR = Path.home() / ".claude-orchestrator"
CONFIG_PATH = CONFIG_DIR / "projects.yaml"
DB_PATH = CONFIG_DIR / "queue.db"


@dataclass
class Project:
    name: str
    path: str
    weight: float
    daily_token_budget: int


def load_projects() -> list[Project]:
    if not CONFIG_PATH.exists():
        print(f"ERROR: {CONFIG_PATH} 없음. 예시 작성하고 다시 실행.", file=sys.stderr)
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        CONFIG_PATH.write_text(
            "projects:\n"
            "  - name: example-saas\n"
            "    path: /home/user/example-saas\n"
            "    weight: 1.0\n"
            "    daily_token_budget: 200000\n"
        )
        sys.exit(1)
    data = yaml.safe_load(CONFIG_PATH.read_text())
    return [Project(**p) for p in data.get("projects", [])]


def get_db() -> sqlite3.Connection:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(DB_PATH)
    db.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
          id INTEGER PRIMARY KEY,
          project TEXT,
          description TEXT,
          priority REAL,
          status TEXT,
          created_at TEXT DEFAULT (datetime('now')),
          finished_at TEXT,
          tokens INTEGER DEFAULT 0
        )
    """)
    return db


def collect_inbox(project: Project) -> list[dict]:
    """프로젝트의 inbox 수집. 실제 구현은 프로젝트별로.
    반환: [{description, urgency(0-1), impact(0-1)}, ...]
    """
    items = []

    # 예시 1: GitHub 이슈 수집 (gh CLI 필요)
    try:
        result = subprocess.run(
            [
                "gh",
                "issue",
                "list",
                "--state",
                "open",
                "--limit",
                "20",
                "--json",
                "number,title,labels",
            ],
            cwd=project.path,
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0:
            import json

            for issue in json.loads(result.stdout):
                labels = [lab["name"] for lab in issue.get("labels", [])]
                if "bug" in labels:
                    items.append(
                        {
                            "description": f"#{issue['number']} {issue['title']}",
                            "urgency": 0.8,
                            "impact": 0.6,
                        }
                    )
                elif "auto-eligible" in labels:
                    items.append(
                        {
                            "description": f"#{issue['number']} {issue['title']}",
                            "urgency": 0.4,
                            "impact": 0.5,
                        }
                    )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    # 예시 2: 스케줄된 정기 작업
    items.append(
        {
            "description": "보안 의존성 점검 (npm audit + 자동 PR)",
            "urgency": 0.3,
            "impact": 0.7,
        }
    )

    return items


def usage_today(db: sqlite3.Connection, project_name: str) -> int:
    today = date.today().isoformat()
    cur = db.execute(
        "SELECT COALESCE(SUM(tokens), 0) FROM jobs WHERE project = ? AND date(created_at) = ?",
        (project_name, today),
    )
    return cur.fetchone()[0]


async def run_job(project: Project, job: dict) -> int:
    cmd = [sys.executable, "automation/router.py", job["description"]]
    print(f"[{project.name}] 실행: {job['description']}", flush=True)
    proc = subprocess.run(
        cmd,
        cwd=project.path,
        capture_output=True,
        text=True,
        timeout=1800,
    )
    if proc.returncode != 0:
        print(f"[{project.name}] 실패 (rc={proc.returncode}): {proc.stderr[:200]}", file=sys.stderr)
    return proc.returncode


async def main() -> int:
    projects = load_projects()
    db = get_db()

    queue = []
    for p in projects:
        if usage_today(db, p.name) >= p.daily_token_budget:
            print(f"[{p.name}] 일일 예산 초과, 건너뜀", flush=True)
            continue
        for item in collect_inbox(p):
            score = p.weight * item.get("urgency", 0.5) * item.get("impact", 0.5)
            queue.append((score, p, item))

    queue.sort(key=lambda x: -x[0])
    print(f"큐 크기: {len(queue)}", flush=True)

    # 상위 N개만
    top_n = int(os.environ.get("SUPERVISOR_TOP_N", "5"))
    for score, p, item in queue[:top_n]:
        rc = await run_job(p, item)
        db.execute(
            "INSERT INTO jobs(project, description, priority, status, finished_at) "
            "VALUES(?, ?, ?, ?, datetime('now'))",
            (p.name, item["description"], score, "ok" if rc == 0 else "fail"),
        )
        db.commit()

    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
