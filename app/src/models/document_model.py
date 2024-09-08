from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class DocumentBase(BaseModel):
    title: str = Field(..., max_length=255)
    author: Optional[str] = Field(None, max_length=255)
    comment: Optional[str] = None
    original_file_name: str = Field(..., max_length=255)


class DocumentCreate(DocumentBase):
    status: Optional[str] = Field("processing", max_length=50)


class DocumentUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    author: Optional[str] = Field(None, max_length=255)
    comment: Optional[str] = None
    status: Optional[str] = Field(None, max_length=50)


class DocumentInDB(DocumentBase):
    document_id: int
    user_id: Optional[int]
    upload_date: datetime

    class Config:
        orm_mode = True


class DocumentResponse(DocumentInDB):
    pass
