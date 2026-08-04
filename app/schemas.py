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
    uploaded_at: datetime

    class Config:
        from_attributes = True

class DocumentStatusUpdate(BaseModel):
    status: str