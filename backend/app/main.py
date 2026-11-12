from contextlib import asynccontextmanager
from fastapi import FastAPI,UploadFile,File,Depends,HTTPException
from sqlalchemy import text
from starlette.middleware.cors import CORSMiddleware
from pathlib import Path
from sqlalchemy.orm import Session
from .db import engine, Base, get_db
from . import models
from .schemas import DocumentOut

UPLOAD_DIR=Path("/code/uploads")
@asynccontextmanager
async def lifespan(app: FastAPI):
    with engine.begin() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    Base.metadata.create_all(bind=engine)
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    yield

app = FastAPI(title="FastAPI", lifespan=lifespan)

@app.get("/health")
def health():
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    return {"status": "ok", "db":"ok"}

@app.post("/documents",response_model=DocumentOut)
async def upload_document(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not  file.filename.lower().endswith(".pdf"):
        raise HTTPException(400,"Only PDF files are allowed!")

    doc = models.Document(filename=file.filename)
    db.add(doc)
    db.commit()
    db.refresh(doc)

    (UPLOAD_DIR / f"{doc.id}.pdf").write_bytes(await file.read())
    return doc

@app.get("/documents", response_model=list[DocumentOut])
def list_documents(db: Session = Depends(get_db)):
    return db.query(models.Document).order_by(models.Document.uploaded_at.desc()).all()

@app.delete("/documents/{doc_id}")
def delete_document(doc_id: int, db: Session = Depends(get_db)):
    doc = db.get(models.Document, doc_id)
    if not doc:
        raise HTTPException(404, "Document not found")
    db.delete(doc)
    db.commit()
    (UPLOAD_DIR / f"{doc.id}.pdf").unlink(missing_ok=True)
    return { "deleted": doc.id }