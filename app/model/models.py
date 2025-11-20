from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    login = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    refresh_token = Column(String(500), nullable=True)
    reset_token = Column(String(500), nullable=True)
    reset_token_expires = Column(DateTime(timezone=True), nullable=True)

    files = relationship("File", back_populates="user")
    chats = relationship("Chat", back_populates="user")

    def __repr__(self):
        return f"<User(id={self.id}, login='{self.login}')>"


class File(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True)
    filename = Column(String(255))
    original_filename = Column(String(255))
    file_path = Column(String(500))
    processed_file_path = Column(String(500), nullable=True)
    file_size = Column(Integer)
    mime_type = Column(String(100))
    status = Column(String(50))  # uploaded, processing, processed, saved
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # null для неавторизованных
    session_id = Column(String(255), nullable=True)  # для неавторизованных
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="files")


class Chat(Base):
    __tablename__ = "chats"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="chats")  # ДОБАВИТЬ
    messages = relationship("Message", back_populates="chat")


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, ForeignKey("chats.id"))
    content = Column(Text)
    role = Column(String(50))  # user, assistant
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    chat = relationship("Chat", back_populates="messages")
