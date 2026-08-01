from fastapi import FastAPI

app = FastAPI()

from fastapi import FastAPI
from sqlalchemy import text
from database import engine

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Document review system is alive"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/db-check")
def db_check():
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    return {"database": "connected"}
