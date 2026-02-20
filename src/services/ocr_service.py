from __future__ import annotations

import structlog

from src.core.config import settings
from src.core.exceptions import OCRError
from src.utils.image_utils import preprocess_for_ocr

logger = structlog.get_logger()


async def extract_text_from_image(image_data: bytes) -> str:
    """Extract text from image using configured OCR provider."""
    preprocessed = preprocess_for_ocr(image_data)

    if settings.OCR_PROVIDER == "google_vision":
        return await _google_vision_ocr(preprocessed)
    return await _tesseract_ocr(preprocessed)


async def _tesseract_ocr(image_data: bytes) -> str:
    """Local Tesseract OCR fallback."""
    import asyncio
    import io

    from PIL import Image

    try:
        import pytesseract

        img = Image.open(io.BytesIO(image_data))
        text = await asyncio.to_thread(pytesseract.image_to_string, img)
        return text.strip()
    except Exception as e:
        await logger.awarning("tesseract_ocr_failed", error=str(e))
        raise OCRError(f"Tesseract OCR failed: {e}") from e


async def _google_vision_ocr(image_data: bytes) -> str:
    """Google Cloud Vision API OCR."""
    import base64

    import httpx

    if not settings.GOOGLE_VISION_API_KEY:
        await logger.awarning("google_vision_not_configured, falling back to tesseract")
        return await _tesseract_ocr(image_data)

    try:
        encoded = base64.b64encode(image_data).decode()
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                f"https://vision.googleapis.com/v1/images:annotate"
                f"?key={settings.GOOGLE_VISION_API_KEY}",
                json={
                    "requests": [
                        {
                            "image": {"content": encoded},
                            "features": [{"type": "TEXT_DETECTION"}],
                        }
                    ]
                },
            )
            resp.raise_for_status()
            data = resp.json()

            annotations = data.get("responses", [{}])[0].get("textAnnotations", [])
            if annotations:
                return annotations[0].get("description", "").strip()
            return ""

    except Exception as e:
        await logger.awarning("google_vision_failed, falling back to tesseract", error=str(e))
        return await _tesseract_ocr(image_data)
