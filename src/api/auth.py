from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm
from src.core.db import get_db
from src.service.auth import UserAuthService
from typing import Annotated
from src.schemas.user import RegisterData

auth_router = APIRouter(prefix="/auth", tags=["Auth"])


def get_auth_servie(db: AsyncSession = Depends(get_db)):
    return UserAuthService(db=db)


@auth_router.post("/login")
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    service: Annotated[UserAuthService, Depends(get_auth_servie)],
):
    user_token = await service.login(form_data=form_data)
    return user_token


@auth_router.post("/register")
async def register_user(
    user_data: RegisterData,
    service: Annotated[UserAuthService, Depends(get_auth_servie)],
):
    return await service.register(user_data=user_data)
