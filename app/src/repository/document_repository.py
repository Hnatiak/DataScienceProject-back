from sqlalchemy.sql import text
from src.models.document_model import DocumentCreate, DocumentInDB
from src.database.db import AsyncSession, get_db

from sqlalchemy.ext.asyncio import AsyncSession
async def create_document_entry(document_data: DocumentCreate, db: AsyncSession) -> int:
    query = text("""
    INSERT INTO Documents (title, author, comment, original_file_name, status)
    VALUES (:title, :author, :comment, :original_file_name, :status)
    RETURNING document_id
    """)
    values = document_data.dict()
    result = await db.execute(query, values)
    document_id = result.scalar()
    return document_id

async def get_document_by_id(document_id: int, db: AsyncSession):
    async with db as session:
        result = await session.execute(
            select(DocumentInDB).where(DocumentInDB.document_id == document_id)
        )
        return result.scalars().first()

async def update_document_status(document_id: int, status: str, db: AsyncSession):
    async with db as session:
        stmt = update(DocumentInDB).where(DocumentInDB.document_id == document_id).values(status=status)
        await session.execute(stmt)
        await session.commit()
