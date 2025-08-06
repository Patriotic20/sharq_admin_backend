from pydantic import BaseModel
from typing import Optional


class RegisterData(BaseModel):
    phone_number: str
    password: str
    role_id: Optional[int] = None


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None
    scopes: list[str] = []
