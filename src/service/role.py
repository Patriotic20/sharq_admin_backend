from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from sharq_models.models.user import Role #type: ignore
from src.schemas.role import RoleBase, RoleCreate, RoleUpdate, RoleResponse
from src.service import BasicCrud


class RoleService(BasicCrud[Role, RoleBase]):
    def __init__(self, db: AsyncSession):
        super().__init__(db)

    async def create_role(self, role_data: RoleCreate) -> RoleResponse:
        existing_role = await self.get_by_field(
            model=Role, field_name="name", field_value=role_data.name
        )
        if existing_role:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Role with this name already exists",
            )

        return await super().create(model=Role, obj_items=role_data)

    async def get_role_by_id(self, role_id: int) -> RoleResponse:
        role = await super().get_by_id(model=Role, item_id=role_id)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Role not found"
            )
        return role

    async def get_all_roles(
        self, limit: int = 100, offset: int = 0
    ) -> List[RoleResponse]:
        return await super().get_all(model=Role, limit=limit, offset=offset)

    async def update_role(self, role_id: int, role_data: RoleUpdate) -> RoleResponse:
        await self.get_role_by_id(role_id)
        return await super().update(model=Role, item_id=role_id, obj_items=role_data)

    async def delete_role(self, role_id: int):
        role = await self.get_role_by_id(role_id)
        if role.users:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete role that is assigned to users",
            )
        return await super().delete(model=Role, item_id=role_id)

    async def get_default_role(self) -> Role:
        stmt = select(Role).where(Role.name == "user")
        result = await self.db.execute(stmt)
        role = result.scalars().first()

        if not role:
            default_role_data = RoleCreate(
                name="user"
            )
            role = await self.create_role(default_role_data)

        return role
