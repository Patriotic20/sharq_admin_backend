from fastapi import APIRouter, Depends
from src.utils.auth import require_roles
from sharq_models import User
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated, List

from src.service.study_lenguage import StudyLanguageCrud
from src.schemas.study_language import (
    StudyLanguageBase,
    StudyLanguageUpdate,
    StudyLanguageResponse,
    StudyLanguageFilter,
)
from src.core.db import get_db

study_language_router = APIRouter(prefix="/study_language", tags=["Study Language"])


def get_service_crud(db: AsyncSession = Depends(get_db)):
    return StudyLanguageCrud(db)


@study_language_router.post("/create", response_model=StudyLanguageResponse)
async def create_study_language(
    item: StudyLanguageBase,
    service: Annotated[StudyLanguageCrud, Depends(get_service_crud)],
    _: Annotated[User, Depends(require_roles(["admin"]))],
):
    return await service.create_study_language(obj=item)


@study_language_router.get(
    "/get_by_id/{language_id}", response_model=StudyLanguageResponse
)
async def get_by_study_language_id(
    language_id: int,
    service: Annotated[StudyLanguageCrud, Depends(get_service_crud)],
    _: Annotated[User, Depends(require_roles(["admin"]))],
):
    return await service.get_by_study_language_id(language_id=language_id)


@study_language_router.get("/get_all", response_model=List[StudyLanguageResponse])
async def get_all_study_languages(
    _: Annotated[User, Depends(require_roles(["admin"]))],
    service: Annotated[StudyLanguageCrud, Depends(get_service_crud)],
    filter_items: StudyLanguageFilter = Depends(),
    limit: int = 20,
    offset: int = 0,
):
    return await service.get_study_language_all(
        filter_obj=filter_items,
        limit=limit,
        offset=offset,
    )


@study_language_router.put(
    "/update/{language_id}", response_model=StudyLanguageResponse
)
async def update_study_language(
    language_id: int,
    update_data: StudyLanguageUpdate,
    service: Annotated[StudyLanguageCrud, Depends(get_service_crud)],
    _: Annotated[User, Depends(require_roles(["admin"]))],
):
    return await service.update_study_language(
        language_id=language_id,
        obj=update_data,
    )


@study_language_router.delete("/delete/{language_id}")
async def delete_study_language(
    language_id: int,
    service: Annotated[StudyLanguageCrud, Depends(get_service_crud)],
    _: Annotated[User, Depends(require_roles(["admin"]))],
):
    return await service.delete_study_language(language_id=language_id)
