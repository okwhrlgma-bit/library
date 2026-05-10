# ADR 0058 — 캐시카우 검증 통과 시 조건부 배포 허용 (PO 명령 2026-05-08)

- 상태: Accepted
- 결정자: PO 조기흠
- 일자: 2026-05-08
- 관계: ADR 0052 부분 supersede (발사 = 보류 → 조건부 허용)

## PO 명령

> "케시카우 자동 수익을 위해 최대한 많은 고민을 해볼것·수익이 확실하며 해당 수익으로 케시카우가 가능하다는 판단시 적용하여 코딩 및 배포 허용"

## 결정

ADR 0052 (코딩 외 활동 0건) **조건부 supersede**:
- 캐시카우 검증 4 조건 모두 충족 = **배포 허용**
- 미달 = 보류 (이전 정책 유지)

## 캐시카우 검증 4 조건 (자동 룰)

1. **시장 점수 ≥ 75** (ADR 0055 게이트 강화·기존 ≥ 60)
2. **캐시카우 점수 ≥ 80** (월정액 + 자동 갱신 + 락인 + 1인 운영)
3. **벤치마크 사례 1+** ($1K MRR+ 솔로 인디 검증·동일/유사 niche)
4. **Q5 PASS** (PIPA·헌법 §3·§14)

```python
def deploy_allowed(market: int, cashcow: int, benchmark_count: int, q5: bool) -> bool:
    return (
        q5
        and market >= 75
        and cashcow >= 80
        and benchmark_count >= 1
    )
```

## 배포 허용 범위

조건 충족 시 = 다음 모두 허용:
- ✅ Streamlit Community Cloud 배포 (₩0)
- ✅ GitHub Pages·Vercel·Netlify 배포 (₩0)
- ✅ 결제 wrapper 활성 (PortOne v2·Stripe·Lemon Squeezy)
- ✅ 도메인 구매·DNS 설정
- ✅ ProductHunt·Hacker News Show HN·X #buildinpublic 발사
- ✅ 사용자 가입 폼·결제 폼 활성

조건 미달 시 = ADR 0052 유지 (코드만·발사 X).

## 차단 유지 (ADR 0052 잔존)

배포 허용 시에도 다음은 차단:
- ❌ 사서 인터뷰 (PO 명시 시만)
- ❌ cold email·전화·외부 미팅
- ❌ 사업자 등록·통신판매업 (PO 외부 작업)
- ❌ NL Cert·Anthropic 키 발급 (PO 외부 작업)
- ❌ 자관 익명화 위반·자관 데이터 누설

## 벤치마크 의무 (PO 명령)

매 캐시카우 후보 = 벤치마크 1+ 인용 의무:
- 솔로 인디 사례 (Pieter Levels·Tony Dinh·Marc Lou·Jon Yongfook·Daniel Vassallo)
- 한국 사례 (삼쩜삼·자비스 등)
- 동일 niche $1K MRR+ 검증

벤치마크 0건 = 배포 허용 X.

## 30 앱 매트릭스 재평가 (Cycle 89)

| 앱 | 시장 | 캐시카우 | 벤치마크 | 배포 가능? |
|---|---:|---:|---|---|
| #1 kormarc-auto | 60 | 70 | MarcEdit·Koha (무료) | ❌ (캐시카우 < 80) |
| #2 kdc-classify | 50 | 65 | X | ❌ (벤치마크 X) |
| #4 librarian-overtime | 55 | 70 | Toggl·RescueTime | ❌ (시장 < 75) |
| **#31 freelancer-tax-helper** | **90** | **100** | **삼쩜삼** | ✅ **배포 허용** |
| **#32 sidehustle-tracker** | **100** | **100** | **Toggl·RescueTime** | ✅ **배포 허용** |

→ **#31·#32 = 4 조건 모두 충족 = 배포 허용 후보**.

## 메모리

- `MEMORY.md` 인덱스 갱신
- `CLAUDE.md §8H` 헌법 박제
- `feedback_conditional_deployment.md` ⭐⭐⭐⭐⭐ (신규)

## 매 사이클 자가 점검

매 신규 앱 = 본 ADR 4 조건 자동 평가:
- 통과 = 배포 코드·인프라 추가 (Streamlit·Stripe wrapper 등)
- 미달 = ADR 0052 유지 (코드만)
