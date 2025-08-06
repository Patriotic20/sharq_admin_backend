from fastapi import APIRouter, Depends
from src.utils.auth import require_roles
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from sharq_models import User #type: ignore
from src.service.education_type import EducationTypeCrud
from src.schemas.education_type import (
    EducationTypeBase,
    EducationTypeUpdate,
    EducationTypeResponse,
    EducationTypeFilter,
)
from src.core.db import get_db

education_type_router = APIRouter(prefix="/education_type", tags=["Education Type"])


def get_service_crud(db: AsyncSession = Depends(get_db)):
    return EducationTypeCrud(db)


@education_type_router.post("/create", response_model=EducationTypeResponse)
async def create_study_form(
    item: EducationTypeBase,
    service: Annotated[EducationTypeCrud, Depends(get_service_crud)],
    _: Annotated[User, Depends(require_roles(["admin"]))],
):
    return await service.create_education_type(obj=item)


@education_type_router.get("/get_by_id/{education_type_id}", response_model=EducationTypeResponse)
async def get_by_study_education_type_id(
    education_type_id: int,
    service: Annotated[EducationTypeCrud, Depends(get_service_crud)],
    _: Annotated[User, Depends(require_roles(["admin"]))],
):
    return await service.get_by_education_type_id(education_id=education_type_id)


@education_type_router.get("/get_all", response_model=list[EducationTypeResponse])
async def get_all_education_type(
    _: Annotated[User, Depends(require_roles(["admin"]))],
    service: Annotated[EducationTypeCrud, Depends(get_service_crud)],
    filter_items: EducationTypeFilter = Depends(),
    limit: int = 20,
    offset: int = 0,
):
    return await service.get_education_type_all(
        filter_obj=filter_items,
        limit=limit,
        offset=offset,
    )


@education_type_router.put("/update/{education_type_id}", response_model=EducationTypeResponse)
async def update_study_form(
    education_type_id: int,
    update_data: EducationTypeUpdate,
    service: Annotated[EducationTypeCrud, Depends(get_service_crud)],
    _: Annotated[User, Depends(require_roles(["admin"]))],
):
    return await service.update_education_type(
        education_id=education_type_id,
        obj=update_data,
    )


@education_type_router.delete("/delete/{education_type_id}")
async def delete_education_type(
    education_type_id: int,
    _: Annotated[User, Depends(require_roles(["admin"]))],
    service: Annotated[EducationTypeCrud, Depends(get_service_crud)],
):
    return await service.delete_education_type(education_id=education_type_id)
