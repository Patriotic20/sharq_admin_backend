from fastapi import APIRouter, Depends
from sharq_models import User #type: ignore
from src.utils.auth import require_roles
from src.service.study_direction import StudyDirectionCrud
from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas.study_direction import (
    StudyDirectionBase,
    StudyDirectionUpdate,
    StudyDirectionResponse,
)
from src.core.db import get_db
from typing import Annotated, List


study_direction_router = APIRouter(prefix="/study_direction", tags=["Study Direction"])


def get_service_crud(db: AsyncSession = Depends(get_db)):
    return StudyDirectionCrud(db)


@study_direction_router.post("/create", response_model=StudyDirectionResponse)
async def create_study_direction(
    item: StudyDirectionBase,
    service: Annotated[StudyDirectionCrud, Depends(get_service_crud)],
    _: Annotated[User, Depends(require_roles(["admin"]))],
):
    return await service.create_study_direction(obj=item)


@study_direction_router.get(
    "/get_by_id/{direction_id}", response_model=StudyDirectionResponse
)
async def get_by_study_direction_id(
    direction_id: int,
    service: Annotated[StudyDirectionCrud, Depends(get_service_crud)],
    _: Annotated[User, Depends(require_roles(["admin"]))],
):
    return await service.get_by_study_direction_id(direction_id=direction_id)


@study_direction_router.get("/get_all", response_model=List[StudyDirectionResponse])
async def get_all_study_directions(
    _: Annotated[User, Depends(require_roles(["admin"]))],
    service: Annotated[StudyDirectionCrud, Depends(get_service_crud)],
    limit: int = 20,
    offset: int = 0,
):
    return await service.get_study_direction_all(
        limit=limit,
        offset=offset,
    )


@study_direction_router.put(
    "/update/{direction_id}", response_model=StudyDirectionResponse
)
async def update_study_direction(
    direction_id: int,
    update_data: StudyDirectionUpdate,
    _: Annotated[User, Depends(require_roles(["admin"]))],
    service: Annotated[StudyDirectionCrud, Depends(get_service_crud)],
):
    return await service.update_study_direction(
        direction_id=direction_id,
        obj=update_data,
    )


@study_direction_router.delete("/delete/{direction_id}")
async def delete_study_direction(
    direction_id: int,
    service: Annotated[StudyDirectionCrud, Depends(get_service_crud)],
    _: Annotated[User, Depends(require_roles(["admin"]))],
):
    return await service.delete_study_direction(direction_id=direction_id)
