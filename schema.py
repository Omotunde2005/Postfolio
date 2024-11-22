from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class UserRegistrationSchema(BaseModel):
    username: str
    email: EmailStr
    password: str
    created_At: datetime = datetime.today()
    last_updated: datetime = datetime.today()

    def dict(self):
        return {
            "username": self.username,
            "email": self.email,
            "password": self.password,
            "created_At": self.created_At,
            "last_updated": self.last_updated
        }


class RefreshTokenSchema(BaseModel):
    token: str

class UpdateUserSchema(BaseModel):
    username: Optional[str] | None = None
    email: Optional[EmailStr] | None = None
    last_updated: datetime = datetime.today()

    def dict(self):
        return {
            "username": self.username,
            "email": self.email,
            "last_updated": self.last_updated
        }


class CreateBoard(BaseModel):
    board_url: str
    title: str
    description: str
    social_app: str
    cta: str
    cta_url: str
    created_At: datetime = datetime.today()
    last_updated: datetime = datetime.today()

    def dict(self):
        return {
            "board_url": self.board_url,
            "title": self.title,
            "description": self.description,
            "social_app": self.social_app,
            "cta": self.cta,
            "cta_url": self.cta_url,
            "created_At": self.created_At,
            "last_updated": self.last_updated
        }

class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

    def dict(self):
        return {
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
            "token_type": self.token_type
        }


class NewPostSchema(BaseModel):
    id: str
    post: str

    def dict(self):
        return {
            "id": self.id,
            "post": self.post
        }


class UpdateBoardSchema(CreateBoard):
    board_url: str | None = None
    title: str | None = None
    description: str | None = None
    social_app: str | None = None
    cta: str | None = None
    cta_url: str | None = None
    last_updated: datetime = datetime.today()

    def dict(self):
        return {
            "board_url": self.board_url,
            "title": self.title,
            "description": self.description,
            "social_app": self.social_app,
            "cta": self.cta,
            "cta_url": self.cta_url,
            "last_updated": self.last_updated
        }

class AddBoardTheme(BaseModel):
    theme: dict

    def dict(self):
        return {
            "theme": self.theme
        }


class HeaderSchema(BaseModel):
    Authorization: str