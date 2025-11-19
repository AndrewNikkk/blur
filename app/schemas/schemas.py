from datetime import datetime

from pydantic import BaseModel, Field


class UserRegister(BaseModel):
    login: str = Field(..., example="Bobor")
    password: str = Field(..., min_length=8, example="password123")


class UserLogin(BaseModel):
    login: str = Field(..., example="Bobor")
    password: str = Field(..., min_length=8, example="password123")


class UserResponse(BaseModel):
    id: int
    login: str
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
