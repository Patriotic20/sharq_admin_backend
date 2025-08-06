import jwt
from datetime import timedelta, timezone, datetime
from typing import Annotated, List

from fastapi import HTTPException, status
from fastapi.params import Depends
from fastapi.security import (
    OAuth2PasswordBearer,
)
from sqlalchemy.orm import joinedload
from sqlalchemy import select 
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext
from pydantic import ValidationError
from jwt.exceptions import InvalidTokenError

from src.schemas.user import TokenData
from src.core.config import settings
from src.core.db import get_db
from sharq_models.models import User


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/auth/login",
)


def hash_password(plain_password: str) -> str:
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


async def authenticate_user(db: AsyncSession, username: str, password: str):
    user_data = await get_user(db=db, username=username)
    if not user_data:
        return None
    if not verify_password(plain_password=password, hashed_password=user_data.password):
        return None
    return user_data


async def get_user(db: AsyncSession, username: str):
    stmt = select(User).options(
        joinedload(User.role)
    ).where(User.phone_number == username)
    
    result = await db.execute(stmt)
    return result.scalars().first()


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: AsyncSession = Depends(get_db),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token, settings.access_secret_key, algorithms=[settings.algorithm]
        )
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        role_id = payload.get("role_id")
        token_data = TokenData(role_id=role_id, username=username)
    except (InvalidTokenError, ValidationError):
        raise credentials_exception

    user = await get_user(db=db, username=token_data.username)
    if user is None:
        raise credentials_exception

    return user


async def get_current_user_with_role(
    required_roles: List[str],
    token: Annotated[str, Depends(oauth2_scheme)],
    db: AsyncSession = Depends(get_db),
):
    user: User = await get_current_user(token=token, db=db)

    if not user.role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="User has no role assigned"
        )

    if user.role.name not in required_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied. Required roles: {required_roles}",
        )

    return user


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.access_token_expire_minutes
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.access_secret_key, algorithm=settings.algorithm
    )
    return encoded_jwt


def require_roles(required_roles: List[str]):
    async def role_checker(
        token: Annotated[str, Depends(oauth2_scheme)],
        db: AsyncSession = Depends(get_db),
    ):
        return await get_current_user_with_role(required_roles, token=token, db=db)

    return role_checker
