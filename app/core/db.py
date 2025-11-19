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
