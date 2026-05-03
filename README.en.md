# kormarc-auto — Korean MARC Auto-Generation SaaS

> **Built by a librarian, for librarians**.
> ISBN → KORMARC `.mrc` in 5 seconds → **KOLAS III·DLS·ALPAS direct import**.
> **Self-library PILOT (1 library·174 files·3,383 records) round-trip 100%** — per-MARC-block disaggregation table below (measured 2026-05-04).

[![release](https://img.shields.io/badge/release-v0.6.0-blue)]() [![tests](https://img.shields.io/badge/tests-662%20passed-brightgreen)]() [![ruff](https://img.shields.io/badge/ruff-0%20errors-brightgreen)]() [![assertions](https://img.shields.io/badge/binary__assertions-39%2F39-brightgreen)]() [![round-trip](https://img.shields.io/badge/round--trip-100%25_(PILOT_1)-brightgreen)]() [![KORMARC](https://img.shields.io/badge/KORMARC-2023.12-blue)]()

**Korean librarians** spend ~8 minutes per record on KORMARC cataloging. kormarc-auto cuts this to ~2 minutes for descriptive blocks. Solo founder (former librarian) shipping after self-library PILOT.

---

## Per-MARC-block accuracy (Self-library PILOT 1·measured 2026-05-04)

| MARC Block | Measurement | Note |
|---|---:|---|
| **Round-trip serialization** | **100%** (3,383 records) | Parser·builder lossless verified |
| 00X Control (001·005·008) | 100% | All records |
| 0XX Bibliographic (020·040·049·056·082·090) | 100% | Avg 4.49 fields/record |
| 245 Title·responsibility | 100% | |
| 250·260·300 Description | 100% | |
| 6XX Subjects·NLSH | 100% (650 auto) | F1 measurement = after NL_CERT_KEY issue |
| 7XX Added entries | 100% | Avg 1.85/record |
| 9XX Local | 100% | |
| 5XX Notes (520·588) | 59.21% | Per-book variance (normal) |
| 4XX·8XX Series | 29.8% | Series-only books |
| 1XX Main entry | 0% (library policy) | This library uses 700 added entries only |
| 880 Hanja parallel | 0% (no Hanja material) | Activates when Hanja arrives |

**Source**: [`docs/eval/results/2026-05-04/per-record.json`](docs/eval/results/2026-05-04/per-record.json) · [`docs/eval/methodology.md`](docs/eval/methodology.md)
**Limitation**: N=1 PILOT·NL_CERT_KEY pending (no external ground-truth match yet)·v0.7 = `kormarc-eval-corpus-v1` 1,000 records public release planned

---

## Quick Start

### 0. 30-second demo (zero API keys·Plan B Cycle 2)

```bash
pip install -e .
KORMARC_DEMO_MODE=1 kormarc-auto demo
```

→ 7 SAMPLE + 5 SENTINEL ISBNs · zero external API calls · 5/5 records · round-trip 100%.

### 1. Install (any OS·Plan B P2 recommended)

```bash
# Recommended: uv tool install (Python 3.12+·any OS)
uv tool install kormarc-auto

# Alternative: pipx
pipx install kormarc-auto

# Windows .venv (legacy .bat compatibility)
setup-once.bat
```

### 2. Initialize

```bash
kormarc-auto init       # creates .env template
# Edit .env, fill in keys
kormarc-auto serve      # FastAPI on :8000
```

---

## CLI Commands

| Command | Purpose |
|---|---|
| `kormarc-auto init` | Create `.env` template (safe·refuses to overwrite existing keys) |
| `kormarc-auto demo` | 30-second offline demo (zero API keys) |
| `kormarc-auto isbn <ISBN>` | ISBN → KORMARC `.mrc` |
| `kormarc-auto batch <file>` | Bulk ISBN list → many `.mrc` |
| `kormarc-auto photo <img1> <img2>` | Cover/colophon photos → KORMARC |
| `kormarc-auto validate <file.mrc>` | Validate existing `.mrc` |
| `kormarc-auto search <query>` | Search by title/author |
| `kormarc-auto serve` | FastAPI REST server |
| `kormarc-auto ui` | Streamlit UI |
| `kormarc-auto info` | Environment + per-MARC-block accuracy table |

Short alias: `ka` (e.g., `ka demo`).

---

## Architecture

- **Stack**: Python 3.12+ · FastAPI · Streamlit · pymarc · Anthropic SDK
- **LLM Provider Router**: Anthropic / Bedrock Seoul (CSAP) / Naver HCX / KT MIDM / LG ExaOne / Azure OpenAI Korea
- **Offline mode**: `KORMARC_DEMO_MODE=1` = 7 SAMPLE_BOOKS + 5 SENTINEL_ISBNs · external calls = 0
- **Provenance**: Auto-stamps KORMARC field 588 (PCC AI provenance) + audit log + hash chain
- **Determinism**: temperature=0·top_p=1·same input → same output
- **Eval corpus v1** (planned): 1,000 records · CC0/NL Korea policy · arXiv preprint
- **Property tests**: 12 invariants (round-trip · 008-40chars · ISBN-13 · KDC↔DDC · tenant)

---

## Constitution (CLAUDE.md hard rules)

- ❌ API keys hardcoded (`.env` only)
- ❌ Aladin attribution missing ("도서 DB 제공 : 알라딘 인터넷서점")
- ❌ "100% automatic" copy (librarian review preserved)
- ❌ External API timeout missing (10s)
- ❌ Korean variable names (identifiers = English)
- ✅ try/except + timeout=10 on external calls
- ✅ confidence score + source_map traceability
- ✅ pymarc UTF-8 explicit
- ✅ Korean docstrings

---

## Plan B autonomous cycles (ADR 0025)

After external 901-source diagnosis (identity fusion + productive avoidance + agent pace inflation + domain expert curse), PO chose **Plan B continuous autonomy** with two preserved invariants:

1. **Constitution violations = 0**: "100% auto" copy / raw probability / body LLM transmission / librarian review bypass = PR auto-blocked
2. **Self-library data git leak = 0**: D:\ data commit attempt = autonomous halt + PO notification (PIPA pre-block)

Cycle = 7 days · P1~P28 queue · ~6.5 months runtime · auto-merge gate (ruff + pytest + binary_assertions + self-library regression ≤ 1pp + demo 30s + constitution 0).

---

## Status (Cycles 1~6 complete)

- 662 tests passing / 6 skipped
- ruff: 0 errors
- binary_assertions: 39/39
- Self-library round-trip baseline: 100% (3,383 records)
- v0.6.0 GitHub tag pushed
- agent_docs/ · 4 reference files (kormarc_field_reference, running_evals, release_process, full backup)

---

## License

Apache-2.0 · See [LICENSE](LICENSE).

## Related

- Korean version: [README.md](README.md)
- Architecture decisions: [docs/adr/](docs/adr/)
- Research: [docs/research/](docs/research/)
- Methodology: [docs/eval/methodology.md](docs/eval/methodology.md)
