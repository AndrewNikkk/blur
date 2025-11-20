from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.auth import verify_password
from app.core.db import delete_file_record, get_db, get_files_by_user, update_user_password
from app.core.storage import delete_file
from app.model.models import Chat, Message, User
from app.routers.auth import get_current_user
from app.schemas.schemas import PasswordChange


router = APIRouter(prefix="/settings", tags=["settings"])


@router.put("/password", status_code=status.HTTP_200_OK)
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Сменить пароль (требует авторизацию)"""
    # Проверяем старый пароль
    if not verify_password(password_data.old_password, current_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect old password")

    # Обновляем пароль
    update_user_password(db, current_user.id, password_data.new_password)

    return {"message": "Password changed successfully"}


@router.delete("/account", status_code=status.HTTP_200_OK)
async def delete_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Удалить аккаунт (требует авторизацию)"""
    user_id = current_user.id

    # Удаляем файлы пользователя (с диска и из БД)
    files = get_files_by_user(db, user_id)
    for file_record in files:
        # Удаляем файлы с диска
        if file_record.file_path:
            delete_file(file_record.file_path)
        if file_record.processed_file_path:
            delete_file(file_record.processed_file_path)
        # Удаляем запись из БД
        delete_file_record(db, file_record.id)

    # Удаляем чат и сообщения пользователя
    chat = db.query(Chat).filter(Chat.user_id == user_id).first()
    if chat:
        messages = db.query(Message).filter(Message.chat_id == chat.id).all()
        for message in messages:
            db.delete(message)
        db.delete(chat)

    # Удаляем пользователя
    db.delete(current_user)
    db.commit()

    return {"message": "Account deleted successfully"}
