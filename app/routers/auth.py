from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.auth import (
    RESET_TOKEN_EXPIRE_HOURS,
    add_token_to_blacklist,
    create_access_token,
    create_refresh_token,
    decode_access_token,
    decode_refresh_token,
    generate_reset_token,
)
from app.core.db import (
    authenticate_user,
    create_user,
    get_db,
    get_user_by_login,
    get_user_by_refresh_token,
    get_user_by_reset_token,
    set_reset_token,
    update_user_password,
    update_user_refresh_token,
)
from app.schemas.schemas import (
    PasswordReset,
    PasswordResetConfirm,
    RefreshToken,
    Token,
    UserLogin,
    UserRegister,
    UserResponse,
)


router = APIRouter(prefix="/auth", tags=["auth"])
security = HTTPBearer()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):

    token = credentials.credentials
    payload = decode_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    login: str = payload.get("sub")

    if login is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = get_user_by_login(db, login)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    existing_user = get_user_by_login(db, user_data.login)
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already registered")

    user = create_user(db, user_data.login, user_data.password)

    return user


@router.post("/login", response_model=Token)
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    user = authenticate_user(db, user_data.login, user_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect login or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user.login})
    refresh_token = create_refresh_token(data={"sub": user.login})

    update_user_refresh_token(db, user.id, refresh_token)

    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.post("/refresh", response_model=Token)
async def refresh_token(token_data: RefreshToken, db: Session = Depends(get_db)):
    payload = decode_refresh_token(token_data.refresh_token)

    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    user = get_user_by_refresh_token(db, token_data.refresh_token)

    if not user or user.refresh_token != token_data.refresh_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    login: str = payload.get("sub")
    if login != user.login:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    new_access_token = create_access_token(data={"sub": user.login})
    new_refresh_token = create_refresh_token(data={"sub": user.login})

    update_user_refresh_token(db, user.id, new_refresh_token)

    return {"access_token": new_access_token, "refresh_token": new_refresh_token, "token_type": "bearer"}


@router.post("/logout")
async def logout(credentials: HTTPAuthorizationCredentials = Depends(security), current_user=Depends(get_current_user)):
    token = credentials.credentials
    add_token_to_blacklist(token)

    return {"message": "Successfully logged out"}


@router.post("/password-reset")
async def password_reset(reset_data: PasswordReset, db: Session = Depends(get_db)):
    user = get_user_by_login(db, reset_data.login)

    if not user:
        return {"message": "If user exists, password reset email would be sent"}

    reset_token = generate_reset_token()
    expires_at = datetime.utcnow() + timedelta(hours=RESET_TOKEN_EXPIRE_HOURS)

    set_reset_token(db, user.login, reset_token, expires_at)

    return {"message": "If user exists, password reset email would be sent", "reset_token": reset_token}


@router.post("/password-reset/confirm", status_code=status.HTTP_200_OK)
async def password_reset_confirm(reset_data: PasswordResetConfirm, db: Session = Depends(get_db)):
    user = get_user_by_reset_token(db, reset_data.reset_token)

    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired reset token")

    update_user_password(db, user.id, reset_data.new_password)

    return {"message": "Password has been reset successfully"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_endpoint(current_user=Depends(get_current_user)):
    return current_user
