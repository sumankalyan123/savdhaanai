from __future__ import annotations

import io

from PIL import Image

from src.core.constants import MAX_IMAGE_SIZE_MB, SUPPORTED_IMAGE_TYPES


def validate_image(data: bytes, content_type: str) -> bool:
    """Validate image data: type, size, and ability to open."""
    if content_type not in SUPPORTED_IMAGE_TYPES:
        return False
    if len(data) > MAX_IMAGE_SIZE_MB * 1024 * 1024:
        return False
    try:
        img = Image.open(io.BytesIO(data))
        img.verify()
        return True
    except Exception:
        return False


def preprocess_for_ocr(data: bytes) -> bytes:
    """Preprocess image for better OCR results."""
    img = Image.open(io.BytesIO(data))

    # Convert to RGB if needed
    if img.mode != "RGB":
        img = img.convert("RGB")

    # Strip EXIF data for privacy
    clean_img = Image.new(img.mode, img.size)
    clean_img.putdata(list(img.getdata()))

    buf = io.BytesIO()
    clean_img.save(buf, format="PNG")
    return buf.getvalue()
