import os
from datetime import datetime, timedelta
from typing import Any, List, Optional, Tuple

from sqlalchemy import create_engine, or_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "app.db")
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ========== ПОЛЬЗОВАТЕЛИ ==========


def get_user_by_login(db: Session, login: str):
    from app.model.models import User

    return db.query(User).filter(User.login == login).first()


def create_user(db: Session, login: str, password: str):
    from app.core.auth import get_password_hash
    from app.model.models import User

    hashed_password = get_password_hash(password)
    db_user = User(login=login, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def authenticate_user(db: Session, login: str, password: str):
    from app.core.auth import verify_password

    user = get_user_by_login(db, login)
    if not user or not verify_password(password, user.hashed_password):
        return False
    return user


def update_user_refresh_token(db: Session, user_id: int, refresh_token: str):
    from app.model.models import User

    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.refresh_token = refresh_token
        db.commit()
        db.refresh(user)
    return user


def set_reset_token(db: Session, login: str, reset_token: str, expires_at):
    user = get_user_by_login(db, login)
    if user:
        user.reset_token = reset_token
        user.reset_token_expires = expires_at
        db.commit()
        db.refresh(user)
    return user


def get_user_by_reset_token(db: Session, reset_token: str):
    from datetime import datetime

    from app.model.models import User

    user = db.query(User).filter(User.reset_token == reset_token).first()
    if user and user.reset_token_expires and user.reset_token_expires > datetime.utcnow():
        return user
    return None


def get_user_by_refresh_token(db: Session, refresh_token: str):
    from app.model.models import User

    return db.query(User).filter(User.refresh_token == refresh_token).first()


def update_user_password(db: Session, user_id: int, new_password: str):
    from app.core.auth import get_password_hash
    from app.model.models import User

    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.hashed_password = get_password_hash(new_password)
        user.reset_token = None
        user.reset_token_expires = None
        db.commit()
        db.refresh(user)
    return user


# ========== ЧАТЫ ==========


def get_or_create_chat(db: Session, user_id: int):
    from app.model.models import Chat

    chat = db.query(Chat).filter(Chat.user_id == user_id).first()
    if not chat:
        chat = Chat(user_id=user_id)
        db.add(chat)
        db.commit()
        db.refresh(chat)
    return chat


def get_chat_by_user(db: Session, user_id: int):
    from app.model.models import Chat

    return db.query(Chat).filter(Chat.user_id == user_id).first()


# ========== СООБЩЕНИЯ ==========


def create_message(db: Session, chat_id: int, content: str, role: str = "user"):
    from app.model.models import Message

    message = Message(chat_id=chat_id, content=content, role=role)
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


def get_messages_by_chat(db: Session, chat_id: int):
    from app.model.models import Message

    return db.query(Message).filter(Message.chat_id == chat_id).order_by(Message.created_at).all()


# ========== ФАЙЛЫ ==========


def create_file(
    db: Session,
    filename: str,
    original_filename: str,
    file_size: int,
    mime_type: str,
    file_path: str,  # 🔹 S3 ключ (соответствует модели)
    user_id: int = None,
    session_id: str = None,
    processed_file_path: str = None,
    status: str = "uploaded",
):
    """Создать запись о файле в БД"""
    from app.model.models import File

    db_file = File(
        filename=filename,
        original_filename=original_filename,
        file_path=file_path,  # ✅ S3 ключ
        processed_file_path=processed_file_path,
        file_size=file_size,
        mime_type=mime_type,
        status=status,
        user_id=user_id,
        session_id=session_id,
    )
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    return db_file


def get_file_by_id(db: Session, file_id: int):
    """Получить файл по ID"""
    from app.model.models import File

    return db.query(File).filter(File.id == file_id).first()


def get_files_by_user(db: Session, user_id: int):
    """Получить все файлы пользователя"""
    from app.model.models import File

    return db.query(File).filter(File.user_id == user_id).order_by(File.created_at.desc()).all()


def get_files_by_session(db: Session, session_id: str):
    """Получить все файлы сессии (для неавторизованных)"""
    from app.model.models import File

    return db.query(File).filter(File.session_id == session_id).order_by(File.created_at.desc()).all()


def get_files_paginated(
    db: Session,
    user_id: int,
    search: Optional[str] = None,
    date_filter: Optional[str] = None,
    size_filter: Optional[str] = None,
    sort: str = "date_desc",
    page: int = 1,
    per_page: int = 10,
) -> Tuple[List, int]:
    """Пагинация файлов с фильтрацией"""
    from app.model.models import File

    query = db.query(File).filter(File.user_id == user_id, File.status.in_(["processed", "saved"]))

    if search:
        search_term = f"%{search}%"
        query = query.filter(or_(File.original_filename.ilike(search_term), File.filename.ilike(search_term)))

    if date_filter:
        now = datetime.now()
        today = datetime(now.year, now.month, now.day)

        if date_filter == "today":
            query = query.filter(File.created_at >= today)
        elif date_filter == "week":
            week_ago = today - timedelta(days=7)
            query = query.filter(File.created_at >= week_ago)
        elif date_filter == "month":
            month_ago = today - timedelta(days=30)
            query = query.filter(File.created_at >= month_ago)

    if size_filter:
        # thresholds are aligned with frontend:
        # small < 100 KB, medium 100 KB..1 MB, large >= 1 MB
        if size_filter == "small":
            query = query.filter(File.file_size < 100 * 1024)
        elif size_filter == "medium":
            query = query.filter(File.file_size >= 100 * 1024, File.file_size < 1024 * 1024)
        elif size_filter == "large":
            query = query.filter(File.file_size >= 1024 * 1024)

    if sort == "date_asc":
        query = query.order_by(File.created_at.asc())
    elif sort == "name_asc":
        query = query.order_by(File.original_filename.asc())
    elif sort == "name_desc":
        query = query.order_by(File.original_filename.desc())
    elif sort == "size_asc":
        query = query.order_by(File.file_size.asc())
    elif sort == "size_desc":
        query = query.order_by(File.file_size.desc())
    else:
        query = query.order_by(File.created_at.desc())

    total = query.count()
    items = query.offset((page - 1) * per_page).limit(per_page).all()

    return items, total


def update_file_status(db: Session, file_id: int, status: str, processed_file_path: str = None):
    """Обновить статус файла"""
    kwargs = {"status": status}
    if processed_file_path:
        kwargs["processed_file_path"] = processed_file_path  # ✅ Исправлено
        kwargs["processed_at"] = datetime.utcnow()

    return update_file(db, file_id, **kwargs)


def delete_file_record(db: Session, file_id: int):
    """Удалить запись о файле из БД"""
    from app.model.models import File

    file = db.query(File).filter(File.id == file_id).first()
    if file:
        db.delete(file)
        db.commit()
    return file


def update_file(db: Session, file_id: int, **kwargs) -> Optional[Any]:
    """Обновляет поля файла"""
    from app.model.models import File

    file = db.query(File).filter(File.id == file_id).first()
    if not file:
        return None

    for key, value in kwargs.items():
        if hasattr(file, key):
            setattr(file, key, value)

    db.commit()
    db.refresh(file)
    return file
