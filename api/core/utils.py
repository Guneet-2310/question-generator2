from fastapi import UploadFile
import fitz
from .config import settings
from fpdf import FPDF
from fpdf.enums import XPos, YPos
import textwrap
import cohere

cohere_client = cohere.Client(settings.cohere_api_key)

def summarize_text(text: str) -> str:
    if len(text) <= 2500:
        return text
    response = cohere_client.summarize(
        text=text,
        length="medium",
        model="summarize-medium"
    )
    return response.summary

async def process_pdf(file: UploadFile) -> str:
    content = await file.read()
    doc = fitz.open(stream=content)
    text = ""
    for page in doc:
        text += page.get_text()
        if len(text) > 3000:
            break
    return " ".join(text.split())[:3000]

def create_pdf(content: str) -> bytes:
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.add_page()

    # Set margins and auto page breaks
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_margins(left=15, top=15, right=15)

    # Set font: try Arial if available, else fallback
    try:
        pdf.add_font("Arial", "", "arial.ttf", uni=True)
        pdf.set_font("Arial", size=12)
    except RuntimeError:
        pdf.set_font("helvetica", size=12)

    # Split content into paragraphs by double line breaks
    for paragraph in content.split("\n\n"):
        if not paragraph.strip():
            pdf.ln(6)
            continue

        # Clean to ASCII-safe content
        safe_text = paragraph.encode("latin-1", "replace").decode("latin-1")

        # Optional wrap: use multi_cell directly for better flow
        try:
            pdf.multi_cell(w=0, h=7, txt=safe_text)
        except Exception:
            # fallback if text has issues
            fallback_text = safe_text[:300]
            pdf.multi_cell(w=0, h=7, txt=fallback_text)

        pdf.ln(4)  # Space between paragraphs

    # Return as bytes
    raw = pdf.output(dest="S")
    return bytes(raw) if isinstance(raw, (bytes, bytearray)) else raw.encode("latin-1")