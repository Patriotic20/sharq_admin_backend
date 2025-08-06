from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Annotated, List
from sqlalchemy.ext.asyncio import AsyncSession

from sharq_models.models import User
from src.service.role import RoleService
from src.schemas.role import RoleCreate, RoleUpdate, RoleResponse, UserRoleUpdate
from src.utils.auth import require_roles
from src.core.db import get_db

role_router = APIRouter(prefix="/role", tags=["Role Management"])


def get_role_service(db: AsyncSession = Depends(get_db)):
    return RoleService(db)


@role_router.post("/create", response_model=RoleResponse)
async def create_role(
    role_data: RoleCreate,
    service: Annotated[RoleService, Depends(get_role_service)],
    _: Annotated[User, Depends(require_roles(["admin"]))],
):
    return await service.create_role(role_data)


@role_router.get("/{role_id}", response_model=RoleResponse)
async def get_role(
    role_id: int,
    service: Annotated[RoleService, Depends(get_role_service)],
    _: Annotated[User, Depends(require_roles(["admin"]))],
):
    return await service.get_role_by_id(role_id)


@role_router.get("/", response_model=List[RoleResponse])
async def get_all_roles(
    service: Annotated[RoleService, Depends(get_role_service)],
    _: Annotated[User, Depends(require_roles(["admin"]))],
    limit: int = Query(100, ge=1),
    offset: int = Query(0, ge=0),
):
    return await service.get_all_roles(limit=limit, offset=offset)


@role_router.put("/{role_id}", response_model=RoleResponse)
async def update_role(
    role_id: int,
    role_data: RoleUpdate,
    service: Annotated[RoleService, Depends(get_role_service)],
    _: Annotated[User, Depends(require_roles(["admin"]))],
):
    return await service.update_role(role_id, role_data)


@role_router.delete("/{role_id}")
async def delete_role(
    role_id: int,
    service: Annotated[RoleService, Depends(get_role_service)],
    _: Annotated[User, Depends(require_roles(["admin"]))],
):
    return await service.delete_role(role_id)


@role_router.put("/user/{user_id}/role", response_model=dict)
async def update_user_role(
    user_id: int,
    role_update: UserRoleUpdate,
    service: Annotated[RoleService, Depends(get_role_service)],
    _: Annotated[User, Depends(require_roles(["admin"]))],
):
    await service.get_role_by_id(role_update.role_id)

    from src.service.auth import UserAuthService

    user_service = UserAuthService(service.db)
    user = await user_service.get_by_id(model=User, item_id=user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.role_id = role_update.role_id
    await service.db.commit()
    await service.db.refresh(user)

    return {
        "message": "User role updated successfully",
        "user_id": user_id,
        "new_role_id": role_update.role_id,
    }
