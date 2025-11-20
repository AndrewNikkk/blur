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
    refresh_token: str
    token_type: str = "bearer"


class RefreshToken(BaseModel):
    refresh_token: str


class PasswordReset(BaseModel):
    login: str = Field(..., example="Bobor")


class PasswordResetConfirm(BaseModel):
    reset_token: str
    new_password: str = Field(..., min_length=8, example="newpassword123")


# class FileUpload(BaseModel):
#     filename: str
#     size: int

# class FileResponse(BaseModel):
#     id: int
#     filename: str
#     original_filename: str
#     file_size: int
#     status: str
#     created_at: datetime
#     processed_at: Optional[datetime]

# class FileProcess(BaseModel):
#     file_id: int

# class FileEdit(BaseModel):
#     content: dict
