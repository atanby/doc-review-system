from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Literal

class DocumentCreate(BaseModel):
    filename: str = Field(min_length=1, max_length=255)

class DocumentResponse(BaseModel):
    id: int
    filename: str
    status: str
    document_type: Optional[str] = None
    extracted_text: Optional[str] = None
    extracted_fields: Optional[str] = None
    uploaded_at: datetime

    class Config:
        from_attributes = True

class DocumentStatusUpdate(BaseModel):
    status: Literal["pending", "approved", "rejected"]
    comment: Optional[str] = None

class ClassifyRequest(BaseModel):
    text: str = Field(min_length=1)

class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8)
    role: Optional[str] = "reviewer"

class UserResponse(BaseModel):
    id: int
    username: str
    role: str

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class StatusHistoryResponse(BaseModel):
    id: int
    document_id: int
    changed_by_id: int
    old_status: str
    new_status: str
    comment: Optional[str] = None
    changed_at: datetime

    class Config:
        from_attributes = True