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
