from typing import Annotated

from fastapi import HTTPException
from fastapi.params import Depends
from fastapi.security import (
    OAuth2PasswordRequestForm,
)
from sqlalchemy.ext.asyncio import AsyncSession

from src.service import BasicCrud
from src.service.role import RoleService
from src.utils import hash_password, authenticate_user, create_access_token
from src.schemas.user import Token, RegisterData
from sharq_models.models import User #type: ignore


class UserAuthService(BasicCrud[User, RegisterData]):
    def __init__(self, db: AsyncSession):
        super().__init__(db)

    async def register(self, user_data: RegisterData):
        if await self.get_by_field(
            model=User, field_name="phone_number", field_value=user_data.phone_number
        ):
            raise HTTPException(status_code=400, detail="User already exists")

        role_service = RoleService(self.db)
        if user_data.role_id:
            await role_service.get_role_by_id(user_data.role_id)
        else:
            default_role = await role_service.get_default_role()
            user_data.role_id = default_role.id

        user_info = RegisterData(
            phone_number=user_data.phone_number,
            password=hash_password(user_data.password),
            role_id=user_data.role_id,
        )
        result = await super().create(model=User, obj_items=user_info)
        return dict(
            message="User created successfully",
            data={
                "user_id": result.id,
                "phone_number": result.phone_number,
                "role_id": result.role_id,
            },
        )


    async def login(
        self, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
    ) -> Token:
        user = await authenticate_user(
            db=self.db, username=form_data.username, password=form_data.password
        )
        if not user:
            raise HTTPException(
                status_code=400, detail="Incorrect username or password"
            )

        access_token = create_access_token(
            data={"sub": user.phone_number, "role_id": user.role_id},
        )

        return Token(access_token=access_token, token_type="bearer")
