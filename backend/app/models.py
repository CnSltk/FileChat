from datetime import datetime
from sqlalchemy import String, Integer, DateTime, ForeignKey,func, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector
from .db import Base

EMBED_DIM = 384 #size of all MiniLM-L6-v2 embeddings

class Document(Base):
    __tablename__ = 'documents'
    id: Mapped[int]=mapped_column(primary_key=True)
    filename: Mapped[str]=mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(20), default = "uploaded")
    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default = func.now())
    chunks = relationship("Chunk", back_populates="document",cascade="all, delete-orphan")
    messages = relationship("Message", back_populates="document",cascade="all, delete-orphan")

class Chunk(Base):
    __tablename__ = 'chunks'
    id: Mapped[int]=mapped_column(primary_key=True)
    document_id: Mapped[int]=mapped_column(ForeignKey('documents.id',ondelete="CASCADE"))
    page: Mapped[int]=mapped_column(Integer)
    text: Mapped[str]=mapped_column(Text)

    embedding: Mapped[list[float] | None] = mapped_column(Vector(EMBED_DIM), nullable=True)
    document=relationship("Document", back_populates="chunks")

class Message(Base):
    __tablename__ = 'messages'
    id: Mapped[int]=mapped_column(primary_key=True)
    document_id: Mapped[int] = mapped_column(ForeignKey('documents.id',ondelete="CASCADE"))
    role: Mapped[str] = mapped_column(String(10))
    content: Mapped[str]=mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    document: Mapped[Document] = relationship("Document", back_populates="messages")