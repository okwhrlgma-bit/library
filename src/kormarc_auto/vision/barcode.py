"""책 표지/뒷면 사진에서 ISBN 바코드 인식.

라이브러리: pyzbar (zbar의 Python 바인딩).
Windows에서 pyzbar 사용 시 zbar.dll 필요 (pip로 자동 설치되지만 별도 안내가 있음).
"""

from __future__ import annotations

import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def extract_isbn_from_image(image_path: str | Path) -> str | None:
    """이미지에서 ISBN-13 바코드 추출.

    Args:
        image_path: 이미지 파일 경로

    Returns:
        13자리 ISBN 또는 None (없거나 인식 실패).
    """
    try:
        from PIL import Image
        from pyzbar.pyzbar import decode
    except ImportError as e:
        logger.error("pyzbar 또는 Pillow 미설치: %s. `pip install pyzbar Pillow`로 설치하세요.", e)
        return None

    try:
        img = Image.open(str(image_path))
    except OSError as e:
        logger.warning("이미지 열기 실패: %s — %s", image_path, e)
        return None

    decoded = decode(img)
    for barcode in decoded:
        data = barcode.data.decode("utf-8", errors="ignore")
        # ISBN-13은 978/979로 시작하는 13자리
        digits = "".join(c for c in data if c.isdigit())
        if len(digits) == 13 and (digits.startswith("978") or digits.startswith("979")):
            logger.info("바코드에서 ISBN 추출: %s", digits)
            return digits

    logger.info("바코드 인식 실패: %s", image_path)
    return None
