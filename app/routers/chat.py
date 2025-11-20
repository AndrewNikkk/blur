from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session

from app.core.db import (
    create_message,
    get_chat_by_user,
    get_db,
    get_messages_by_chat,
    get_or_create_chat,
)
from app.model.models import User
from app.routers.auth import get_current_user
from app.schemas.schemas import ChatResponse, ChatWithMessages, MessageCreate, MessageResponse


router = APIRouter(prefix="/chat", tags=["chat"])
security = HTTPBearer()


@router.get("", response_model=ChatResponse)
async def get_chat(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Получить чат пользователя (требует авторизацию)"""
    chat = get_or_create_chat(db, current_user.id)
    return chat


@router.get("/messages", response_model=ChatWithMessages)
async def get_chat_messages(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Получить все сообщения чата пользователя (требует авторизацию)"""
    chat = get_or_create_chat(db, current_user.id)
    messages = get_messages_by_chat(db, chat.id)

    return ChatWithMessages(
        id=chat.id,
        user_id=chat.user_id,
        created_at=chat.created_at,
        messages=[MessageResponse.model_validate(m) for m in messages],
    )


@router.post("/message", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def send_message(
    message_data: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Отправить сообщение в чат (требует авторизацию)"""
    chat = get_or_create_chat(db, current_user.id)

    # Создаем сообщение пользователя
    user_message = create_message(db, chat.id, message_data.content, role="user")

    # Здесь можно добавить логику для ответа ассистента
    # Например, вызов AI API для генерации ответа
    # assistant_response = await get_ai_response(message_data.content)
    # create_message(db, chat.id, assistant_response, role="assistant")

    return user_message


@router.delete("")
async def delete_chat(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Удалить чат пользователя (требует авторизацию)"""
    # from app.model.models import Chat, Message

    chat = get_chat_by_user(db, current_user.id)

    if not chat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")

    # Удаляем все сообщения чата
    messages = get_messages_by_chat(db, chat.id)
    for message in messages:
        db.delete(message)

    # Удаляем сам чат
    db.delete(chat)
    db.commit()

    return {"message": "Chat deleted successfully"}
