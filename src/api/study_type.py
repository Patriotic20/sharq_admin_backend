from fastapi import APIRouter, Depends
from src.utils.auth import require_roles
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from sharq_models import User #type: ignore
from src.service.study_type import StudyTypeCrud
from src.schemas.study_form import (
    StudyFormBase,
    StudyFormUpdate,
    StudyFormResponse,
    StudyFormFilter,
)
from src.core.db import get_db

study_type_router = APIRouter(prefix="/study_type", tags=["Study Type"])


def get_service_crud(db: AsyncSession = Depends(get_db)):
    return StudyTypeCrud(db)


@study_type_router.post("/create", response_model=StudyFormResponse)
async def create_study_type(
    item: StudyFormBase,
    service: Annotated[StudyTypeCrud, Depends(get_service_crud)],
    _: Annotated[User, Depends(require_roles(["admin"]))],
):
    return await service.create_study_type(obj=item)


@study_type_router.get("/get_by_id/{form_id}", response_model=StudyFormResponse)
async def get_by_study_type_id(
    type_id: int,
    service: Annotated[StudyTypeCrud, Depends(get_service_crud)],
    _: Annotated[User, Depends(require_roles(["admin"]))],
):
    return await service.get_by_study_type_id(
        study_id=type_id
    )


@study_type_router.get("/get_all", response_model=list[StudyFormResponse])
async def get_all_study_type(
    _: Annotated[User, Depends(require_roles(["admin"]))],
    service: Annotated[StudyTypeCrud, Depends(get_service_crud)],
    filter_items: StudyFormFilter = Depends(),
    limit: int = 20,
    offset: int = 0,
):
    return await service.get_study_type_all(
        filter_obj=filter_items,
        limit=limit,
        offset=offset,
    )


@study_type_router.put("/update/{form_id}", response_model=StudyFormResponse)
async def update_study_type(
    type_id: int,
    update_data: StudyFormUpdate,
    service: Annotated[StudyTypeCrud, Depends(get_service_crud)],
    _: Annotated[User, Depends(require_roles(["admin"]))],
):
    return await service.update_study_type(
        study_id=type_id,
        obj=update_data,
    )


@study_type_router.delete("/delete/{form_id}")
async def delete_study_type(
    type_id: int,
    _: Annotated[User, Depends(require_roles(["admin"]))],
    service: Annotated[StudyTypeCrud, Depends(get_service_crud)],
):
    return await service.delete_study_type(study_id=type_id)
