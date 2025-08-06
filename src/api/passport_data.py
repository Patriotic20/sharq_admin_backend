from fastapi import APIRouter, Depends
from src.utils.auth import require_roles
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from sharq_models import User #type: ignore
from src.service.passport_data import PassportDataCrud
from src.schemas.passport_data import (
    PassportDataUpdate,
    PassportDataResponse,
)
from src.core.db import get_db

passport_data_router = APIRouter(prefix="/passport_data", tags=["Passport Data"])


def get_service_crud(db: AsyncSession = Depends(get_db)):
    return PassportDataCrud(db)





@passport_data_router.get("/get_by_id/{passport_data_id}", response_model=PassportDataResponse)
async def get_by_passport_data_id(
    passport_data_id: int,
    service: Annotated[PassportDataCrud, Depends(get_service_crud)],
    _: Annotated[User, Depends(require_roles(["admin"]))],
):
    return await service.get_passport_data_by_id(
        passport_data_id=passport_data_id
    )


@passport_data_router.get("/get_all", response_model=list[PassportDataResponse])
async def get_all_passport_datas(
    _: Annotated[User, Depends(require_roles(["admin"]))],
    service: Annotated[PassportDataCrud, Depends(get_service_crud)],
    limit: int = 20,
    offset: int = 0,
):
    return await service.get_all_passport_data(
        limit=limit,
        offset=offset,
    )


@passport_data_router.put("/update/{passport_data_id}", response_model=PassportDataResponse)
async def update_passport_data(
    passport_data_id: int,
    update_data: PassportDataUpdate,
    service: Annotated[PassportDataCrud, Depends(get_service_crud)],
    _: Annotated[User, Depends(require_roles(["admin"]))],
):
    return await service.update_passport_data(
        passport_data_id=passport_data_id,
        obj=update_data,
    )


@passport_data_router.delete("/delete/{passport_data_id}")
async def delete_passport_data(
    passport_data_id: int,
    _: Annotated[User, Depends(require_roles(["admin"]))],
    service: Annotated[PassportDataCrud, Depends(get_service_crud)],
):
    return await service.delete_passport_data(passport_data_id=passport_data_id)
