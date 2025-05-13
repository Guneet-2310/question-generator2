from fastapi import APIRouter, UploadFile, HTTPException, status, Query
from fastapi.responses import StreamingResponse
from io import BytesIO
from api.core.utils import process_pdf, summarize_text, create_pdf
from api.core.config import settings
import cohere
import asyncio

# 1. Initialize router first
router = APIRouter(prefix="/generate", tags=["generator"])
cohere_client = cohere.Client(settings.cohere_api_key)

# Add this new endpoint ABOVE the existing PDF endpoint
@router.post("/questions/text")
async def generate_questions_text(
    file: UploadFile,
    num_mcqs: int = Query(3, ge=1, le=10),
    num_shortans: int = Query(2, ge=1, le=5),
    difficulty: str = Query("Easy", pattern="^(Easy|Medium|Hard)$")
):
    if file.content_type not in settings.allowed_file_types:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Only PDF files are allowed"
        )

    try:
        text = await process_pdf(file)
        summary = summarize_text(text)
        
        prompt = f"""Generate {num_mcqs} MCQs and {num_shortans} short-answer questions.
        Difficulty: {difficulty}
        Content: {summary}
        Format: **Questions:** (list questions) \n\n**Answers:** (list answers)"""
        
        response = cohere_client.generate(
            model='command',
            prompt=prompt,
            temperature=0.5,
            max_tokens=800
        )
        
        return {
            "questions": response.generations[0].text,
            "status": "success"
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating questions: {str(e)}"
        )

@router.post("/questions")
async def generate_questions(
    file: UploadFile,
    num_mcqs: int = Query(3, ge=1, le=10),
    num_shortans: int = Query(2, ge=1, le=5),
    difficulty: str = Query("Easy", pattern="^(Easy|Medium|Hard)$")
):
    if file.content_type not in settings.allowed_file_types:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Only PDF files are allowed"
        )

    try:
        text = await process_pdf(file)
        summary = summarize_text(text)
        
        # Fixed parameter references
        prompt = f"""Generate {num_mcqs} MCQs and {num_shortans} short-answer questions.
        Difficulty: {difficulty}
        Content: {summary}
        Format: **Questions:** (list questions) \n\n**Answers:** (list answers)"""
        
        response = cohere_client.generate(
            model='command',
            prompt=prompt,
            temperature=0.5,
            max_tokens=800
        )
        
        raw_content = response.generations[0].text
        clean_content = "".join([c if ord(c) < 128 else '?' for c in raw_content])
        
        pdf_bytes = create_pdf(clean_content)  # Modified line
        
        return StreamingResponse(
            BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=questions.pdf"}
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating questions: {str(e)}"
        )
        
@router.post("/questions/pdf")
async def generate_questions_pdf(file: UploadFile):
    try:
        # 1) pull text out of the PDF
        text = await process_pdf(file)

        # 2) summarize / generate questions
        summary = summarize_text(text)

        # 3) turn that summary into a PDF bytestring
        pdf_bytes = create_pdf(summary)

        # 4) return it as a download
        return StreamingResponse(
            BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content‑Disposition": "attachment; filename=questions.pdf"
            }
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating PDF: {e}"
        )