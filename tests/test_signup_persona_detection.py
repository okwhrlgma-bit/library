"""signup.detect_persona — 도서관명·이메일 도메인 4 페르소나 자동 분류 테스트."""

from __future__ import annotations

from kormarc_auto.server.signup import detect_persona


def test_school_libraries_classified_general():
    assert detect_persona("a@b.com", "서울 ○○초등학교 도서관") == "general"
    assert detect_persona("b@b.com", "○○고등학교 도서관") == "general"


def test_small_libraries_classified_general():
    assert detect_persona("c@b.com", "○○동네 작은도서관") == "general"
    assert detect_persona("d@b.com", "마을 도서관") == "general"


def test_university_classified_acquisition():
    assert detect_persona("a@kaist.ac.kr", "KAIST 도서관") == "acquisition"
    assert detect_persona("b@harvard.edu", "Harvard Library") == "acquisition"
    assert detect_persona("c@b.com", "○○대학교 중앙도서관") == "acquisition"


def test_special_libraries_classified_acquisition():
    assert detect_persona("a@b.com", "○○법무법인 자료실") == "acquisition"
    assert detect_persona("b@b.com", "○○병원 의학도서관") == "acquisition"
    assert detect_persona("c@b.com", "○○연구원 자료실") == "acquisition"


def test_government_classified_general():
    assert detect_persona("a@kma.go.kr", None) == "general"


def test_video_libraries_classified_video():
    assert detect_persona("a@b.com", "○○ 영상 자료관") == "video"


def test_unknown_default():
    assert detect_persona("user@gmail.com", None) == "unknown"
    assert detect_persona("a@b.com", "○○도서관") == "unknown"  # 일반 명칭만
