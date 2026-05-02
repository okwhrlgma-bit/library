"""24시간 AI 사서 비서 (Librarian Agent) — Part 73 (P14·P15) 정합.

사서 페인 (Part 73·76·77):
- 야간·순회사서 = 혼자 = 도움 받을 동료 X
- 감정노동 67.9% = 응대 부담
- 자관 정보 모름 = 추정 작업

해결: AI Agent = 자관 KB 검색·KORMARC 기본·이용자 응대 1차.
폭언 자동 감지 → IncidentLogger 연계.

Phase 1 = 규칙 기반 + KB 검색.
Phase 2 = Anthropic Agent SDK (Mem0 통합).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from kormarc_auto.intelligence.library_knowledge_base import LibraryKnowledgeBase
from kormarc_auto.safety.incident_logger import Incident, IncidentLogger, detect_abuse


@dataclass
class AgentResponse:
    """Agent 응답."""

    answer: str
    confidence: float  # 0.0~1.0
    needs_librarian: bool = False  # 사서 검토 필요
    incident_detected: bool = False  # 폭언·민원 감지


class LibrarianAgent:
    """24시간 AI 사서 비서.

    사용:
        agent = LibrarianAgent(sasagwan='○○도서관', kb_dir=Path('.cache/kb'), incident_dir=Path('.cache/incidents'))
        resp = agent.ask("EQ vs CQ prefix 차이?")
        # 또는 이용자 응대
        resp = agent.respond_to_patron("이 책 어디 있어요?", librarian_name='홍길동')
    """

    def __init__(
        self,
        *,
        sasagwan: str,
        kb_dir: Path,
        incident_dir: Path,
    ) -> None:
        self.sasagwan = sasagwan
        self.kb = LibraryKnowledgeBase(kb_dir)
        self.incident_logger = IncidentLogger(incident_dir)

    def ask(self, question: str) -> AgentResponse:
        """사서 질문 → 자관 KB 검색·답변.

        예: "EQ vs CQ prefix 차이?" → KB 검색 결과
        """
        # 1. 자관 KB 검색
        decisions = self.kb.query(self.sasagwan, question, limit=3)
        if decisions:
            answer_parts = [
                f"이전 결정 ({d.timestamp[:10]}):\n- {d.decision}"
                + (f"\n  이유: {d.reason}" if d.reason else "")
                for d in decisions
            ]
            return AgentResponse(
                answer="\n\n".join(answer_parts),
                confidence=0.85,
                needs_librarian=False,
            )

        # 2. KORMARC 표준 질문 매칭 (Phase 1·휴리스틱)
        std_answer = self._match_standard_question(question)
        if std_answer:
            return AgentResponse(answer=std_answer, confidence=0.75)

        # 3. 답변 X = 사서 검토 필요
        return AgentResponse(
            answer="죄송합니다. 자관 KB·표준 매뉴얼에 답이 없어요. 사서 선생님 검토가 필요합니다.",
            confidence=0.0,
            needs_librarian=True,
        )

    def respond_to_patron(
        self,
        patron_message: str,
        *,
        librarian_name: str = "(사서 부재)",
    ) -> AgentResponse:
        """이용자 응대 1차 답변.

        - 일반 질문 (운영시간·자료 검색·이용 안내) = 자동
        - 폭언·성희롱 자동 감지 = IncidentLogger 자동 기록
        - 어려운 질문 = 사서 escalate
        """
        # 1. 폭언·성희롱 감지 (Part 77 정합·서울시 7대 지침)
        abuse = detect_abuse(patron_message)
        if abuse and abuse.get("detected"):
            incident = Incident(
                sasagwan=self.sasagwan,
                librarian_name=librarian_name,
                incident_type=abuse["type"],
                description=patron_message[:200],
                severity=3,
            )
            self.incident_logger.log(incident)
            return AgentResponse(
                answer=(
                    "본 응대는 자동 기록되었어요. 도서관 운영 정책에 따라 "
                    "정중한 의사소통을 부탁드립니다. 사서 선생님께 즉시 연락드릴게요."
                ),
                confidence=1.0,
                needs_librarian=True,
                incident_detected=True,
            )

        # 2. 일반 응대 매칭
        std = self._match_patron_question(patron_message)
        if std:
            return AgentResponse(answer=std, confidence=0.8)

        # 3. 어려운 질문 = escalate
        return AgentResponse(
            answer="확인 후 사서 선생님께서 자세히 답변드리겠습니다. 잠시만 기다려주세요.",
            confidence=0.4,
            needs_librarian=True,
        )

    def _match_standard_question(self, question: str) -> str | None:
        """KORMARC·KDC·운영 표준 질문 매칭."""
        q = question.lower()
        if "008" in q and ("자리" in q or "필드" in q):
            return "008 필드 = 정확히 40자리. 06=발행상태, 07-10=발행연도1, 35-37=언어부호."
        if "880" in q and ("한자" in q or "880" in q):
            return (
                "880 = 대체문자 표제 (한자·로마자). NLK 「로마자 표기 지침(2021)」 RR 기본·MR 학술."
            )
        if "kdc" in q or "분류" in q:
            return "KDC 6판 정합. AI 추천 = 사서 검토 후 사용. 신주제 = 자관 결정 누적 (KB)."
        if "049" in q or "청구기호" in q:
            return "049 = 자관 청구기호. ▾l 등록번호, ▾c 복본, ▾f 별치, ▾v 권차."
        return None

    def _match_patron_question(self, message: str) -> str | None:
        """이용자 일반 질문 매칭."""
        m = message.lower()
        if any(kw in m for kw in ["운영시간", "여는 시간", "닫는 시간"]):
            return "도서관 운영시간은 홈페이지·도서관 입구 안내판에서 확인하실 수 있어요."
        if any(kw in m for kw in ["대출", "빌리", "반납"]):
            return "대출·반납은 1층 안내데스크에서 가능합니다. 회원증 또는 신분증을 가져오세요."
        if any(kw in m for kw in ["휴관", "쉬는 날"]):
            return "정기 휴관일 = 매월 첫째 월요일·법정 공휴일."
        if any(kw in m for kw in ["주차", "주차장"]):
            return "주차 안내는 도서관 1층 안내데스크 또는 홈페이지에서 확인하세요."
        return None


__all__ = ["AgentResponse", "LibrarianAgent"]
