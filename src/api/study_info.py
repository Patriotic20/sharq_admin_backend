from fastapi import APIRouter, Depends
from src.service.study_info import StudyInfoCrud
from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas.study_info import StudyInfoResponse
from src.core.db import get_db
from sharq_models import User #type: ignore
from src.utils.auth import require_roles
from typing import Annotated

study_info_router = APIRouter(prefix="/study_info", tags=["Study Info"])


def get_service_crud(db: AsyncSession = Depends(get_db)):
    return StudyInfoCrud(db)


@study_info_router.get("/get_by_id/{study_info_id}")
async def get_by_study_info_id(
    study_info_id: int,
    service: Annotated[StudyInfoCrud, Depends(get_service_crud)],
    _: Annotated[User, Depends(require_roles(["admin"]))],
) -> StudyInfoResponse:
    return await service.get_study_info_by_id(study_info_id=study_info_id)


@study_info_router.get("/get_all")
async def get_all_study_info(
    service: Annotated[StudyInfoCrud, Depends(get_service_crud)],
    _: Annotated[User, Depends(require_roles(["admin"]))],
    limit: int | None = 20,
    offset: int | None = 0,
) -> list[StudyInfoResponse]:
    return await service.get_all_study_info(
        limit=limit, offset=offset
    )


