from typing import Optional
from fastapi import APIRouter, Depends, UploadFile, HTTPException, File
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.db import get_db
from src.repository.document_repository import create_document_entry
from src.services.pdf_service import process_pdf, vectorize_text
from src.models.document_model import DocumentCreate

router = APIRouter()

@router.post("/documents/")
async def upload_document(
    title: str,
    original_file_name: str,
    file: UploadFile = File(...),
    author: Optional[str] = None,
    comment: Optional[str] = None,
    status: Optional[str] = "processing",
    db: AsyncSession = Depends(get_db)
):
    try:
        # Process the PDF file
        extracted_text = process_pdf(file)
        # print(extracted_text) ##

        # Create a document entry in the database
        document_data = DocumentCreate(
            title=title,
            author=author,
            comment=comment,
            original_file_name=original_file_name,
            status=status
        )
        # document_id = await create_document_entry(document_data, db)

        # Vectorize the extracted text
        text_vector = vectorize_text(extracted_text)
        # print(text_vector)
        # document = await get_document_by_id(document_id, db)
        return document

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
