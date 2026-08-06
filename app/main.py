from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List

from database import engine, get_db
import models
import schemas
from auth import hash_password, verify_password, create_access_token
from dependencies import get_current_user, require_role
from classify import predict_document_type
from fastapi import UploadFile, File
from extraction import extract_text
from fields import extract_fields, fields_to_json

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Document review system is alive"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/db-check")
def db_check(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"database": "connected"}

# ---- Auth endpoints ----

@app.post("/register", response_model=schemas.UserResponse)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.username == user.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already taken")
    new_user = models.User(
        username=user.username,
        hashed_password=hash_password(user.password),
        role=user.role,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    token = create_access_token(data={"sub": user.username, "role": user.role})
    return {"access_token": token, "token_type": "bearer"}

# ---- Document CRUD (now with protection where it matters) ----

@app.post("/documents", response_model=schemas.DocumentResponse)
def create_document(
    document: schemas.DocumentCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    new_doc = models.Document(filename=document.filename)
    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)
    return new_doc

@app.get("/documents", response_model=List[schemas.DocumentResponse])
def list_documents(
    status: str = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    query = db.query(models.Document)
    if status:
        query = query.filter(models.Document.status == status)
    return query.all()

@app.get("/documents/{document_id}", response_model=schemas.DocumentResponse)
def get_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    doc = db.query(models.Document).filter(models.Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc

@app.patch("/documents/{document_id}/status", response_model=schemas.DocumentResponse)
def update_status(
    document_id: int,
    update: schemas.DocumentStatusUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role("reviewer")),
):
    doc = db.query(models.Document).filter(models.Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    doc.status = update.status
    db.commit()
    db.refresh(doc)
    return doc
@app.post("/documents/upload", response_model=schemas.DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    file_bytes = await file.read()

    try:
        text = extract_text(file.filename, file_bytes)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    fields = extract_fields(text)

    new_doc = models.Document(
        filename=file.filename,
        extracted_text=text,
        extracted_fields=fields_to_json(fields),
    )
    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)
    return new_doc

@app.delete("/documents/{document_id}")
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role("admin")),
):
    doc = db.query(models.Document).filter(models.Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    db.delete(doc)
    db.commit()
    return {"message": "Document deleted"}
@app.post("/documents/{document_id}/classify", response_model=schemas.DocumentResponse)
def classify_document(
    document_id: int,
    request: schemas.ClassifyRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    doc = db.query(models.Document).filter(models.Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    predicted_type = predict_document_type(request.text)
    doc.document_type = predicted_type
    db.commit()
    db.refresh(doc)
    return doc
