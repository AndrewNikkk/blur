import os

from sqlalchemy import create_engine
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
    # from app.model.models import User

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


def get_or_create_chat(db: Session, user_id: int):
    """Получить или создать чат для пользователя"""
    from app.model.models import Chat

    chat = db.query(Chat).filter(Chat.user_id == user_id).first()

    if not chat:
        chat = Chat(user_id=user_id)
        db.add(chat)
        db.commit()
        db.refresh(chat)

    return chat


def create_message(db: Session, chat_id: int, content: str, role: str = "user"):
    """Создать сообщение в чате"""
    from app.model.models import Message

    message = Message(chat_id=chat_id, content=content, role=role)
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


def get_messages_by_chat(db: Session, chat_id: int):
    """Получить все сообщения чата"""
    from app.model.models import Message

    return db.query(Message).filter(Message.chat_id == chat_id).order_by(Message.created_at).all()


def get_chat_by_user(db: Session, user_id: int):
    """Получить чат пользователя"""
    from app.model.models import Chat

    return db.query(Chat).filter(Chat.user_id == user_id).first()


def create_file(
    db: Session,
    filename: str,
    original_filename: str,
    file_path: str,
    file_size: int,
    mime_type: str,
    user_id: int = None,
    session_id: str = None,
):
    """Создать запись о файле в БД"""
    from app.model.models import File

    db_file = File(
        filename=filename,
        original_filename=original_filename,
        file_path=file_path,
        file_size=file_size,
        mime_type=mime_type,
        status="uploaded",
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


def update_file_status(db: Session, file_id: int, status: str, processed_file_path: str = None):
    """Обновить статус файла"""
    from datetime import datetime

    from app.model.models import File

    file = db.query(File).filter(File.id == file_id).first()
    if file:
        file.status = status
        if processed_file_path:
            file.processed_file_path = processed_file_path
        if status == "processed":
            file.processed_at = datetime.utcnow()
        db.commit()
        db.refresh(file)
    return file


def delete_file_record(db: Session, file_id: int):
    """Удалить запись о файле из БД"""
    from app.model.models import File

    file = db.query(File).filter(File.id == file_id).first()
    if file:
        db.delete(file)
        db.commit()
    return file


def update_file_user_id(db: Session, file_id: int, user_id: int):
    """Обновить user_id файла (например, когда неавторизованный пользователь регистрируется)"""
    from app.model.models import File

    file = db.query(File).filter(File.id == file_id).first()
    if file:
        file.user_id = user_id
        file.session_id = None  # Убираем session_id, так как теперь есть user_id
        db.commit()
        db.refresh(file)
    return file
