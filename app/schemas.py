from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class DocumentCreate(BaseModel):
    filename: str

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
    status: str
    comment: Optional[str] = None

class ClassifyRequest(BaseModel):
    text: str

class UserCreate(BaseModel):
    username: str
    password: str
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