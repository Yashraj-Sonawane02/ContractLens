import io
import os
import logging
import numpy as np
from typing import Dict, Any, List
from PIL import Image
import fitz  # PyMuPDF
from app.core.config import settings

logger = logging.getLogger(__name__)

# Check RapidOCR (ONNX engine - pure python local fallback)
try:
    from rapidocr_onnxruntime import RapidOCR
    rapid_ocr_engine = RapidOCR()
    HAS_RAPID_OCR = True
except Exception as e:
    logger.warning(f"Could not initialize RapidOCR: {e}")
    HAS_RAPID_OCR = False

# Check pytesseract availability
try:
    import pytesseract
    HAS_PYTESSERACT = True
except ImportError:
    HAS_PYTESSERACT = False

# Check google.genai availability
try:
    from google import genai
    from google.genai import types
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False

def extract_text_from_image_bytes(image_bytes: bytes) -> str:
    """
    Extracts text from raw image bytes using a 3-stage OCR pipeline:
    Stage 1: Google Gemini AI Vision OCR (high accuracy on scanned contracts & stamp papers)
    Stage 2: RapidOCR ONNX local Engine (100% local, fast pure-Python OCR)
    Stage 3: Pytesseract local OCR fallback
    """
    api_key = os.getenv("GEMINI_API_KEY", "").strip() or getattr(settings, "GEMINI_API_KEY", "").strip()
    use_llm = HAS_GENAI and api_key and len(api_key) > 15 and "your_" not in api_key.lower()

    # Stage 1: Gemini AI Vision OCR
    if use_llm:
        models_to_try = ["gemini-flash-latest", "gemini-3.6-flash", "gemini-3.5-flash", "gemini-2.5-flash"]
        for m_name in models_to_try:
            try:
                client = genai.Client(api_key=api_key)
                prompt = (
                    "You are a specialized legal OCR engine. Perform optical character recognition (OCR) "
                    "on this scanned legal contract document image. Extract ALL text word-for-word accurately, "
                    "preserving section numbers, clause headings, names, dates, and paragraph structures. "
                    "Do not summarize or omit any terms."
                )
                image_part = types.Part.from_bytes(data=image_bytes, mime_type="image/png")
                response = client.models.generate_content(
                    model=m_name,
                    contents=[image_part, prompt]
                )
                if response and response.text and len(response.text.strip()) > 10:
                    logger.info(f"Successfully extracted OCR text via Gemini Vision ({m_name})")
                    return response.text.strip()
            except Exception as e:
                err_str = str(e)
                if "RESOURCE_EXHAUSTED" in err_str or "429" in err_str:
                    logger.warning(f"Gemini Vision API quota hit on {m_name}. Switching to local RapidOCR.")
                    break
                logger.warning(f"Gemini Vision OCR error with model {m_name}: {e}")
                continue

    # Stage 2: RapidOCR Local ONNX Engine
    if HAS_RAPID_OCR:
        try:
            img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            img_np = np.array(img)
            result, _ = rapid_ocr_engine(img_np)
            if result:
                lines = [line[1] for line in result if len(line) > 1 and line[1].strip()]
                text = "\n".join(lines)
                if text and len(text.strip()) > 10:
                    logger.info("Successfully extracted OCR text via local RapidOCR engine")
                    return text.strip()
        except Exception as ex:
            logger.warning(f"RapidOCR local engine error: {ex}")

    # Stage 3: Pytesseract local OCR fallback
    if HAS_PYTESSERACT:
        try:
            img = Image.open(io.BytesIO(image_bytes))
            text = pytesseract.image_to_string(img)
            if text and len(text.strip()) > 10:
                logger.info("Successfully extracted OCR text via Pytesseract")
                return text.strip()
        except Exception as ex:
            logger.warning(f"Pytesseract local OCR fallback error: {ex}")

    return ""

def perform_ocr_on_pdf_bytes(pdf_bytes: bytes) -> Dict[str, Any]:
    """
    Renders scanned PDF pages to high-resolution PNG images using PyMuPDF (fitz)
    and executes OCR extraction across all scanned pages.
    """
    full_ocr_text = ""
    pages_processed = 0

    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        pages_processed = len(doc)
        for page_num in range(pages_processed):
            page = doc[page_num]
            # Render page at 200 DPI for high OCR clarity
            pix = page.get_pixmap(dpi=200)
            img_bytes = pix.tobytes("png")

            page_text = extract_text_from_image_bytes(img_bytes)
            if page_text:
                full_ocr_text += f"\n--- Page {page_num + 1} (OCR Extracted) ---\n" + page_text
        doc.close()
    except Exception as e:
        logger.error(f"Failed to render scanned PDF pages for OCR: {e}")

    return {
        "text": full_ocr_text.strip(),
        "total_pages": pages_processed,
        "ocr_used": True
    }
