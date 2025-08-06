from fastapi import APIRouter, Depends, Query
from src.service.user_data import UserData
from src.core.db import get_db
from src.schemas.user_data import UserDataFilterByPassportData, UserDataFilterByStudyInfo
from sharq_models import User  # type: ignore
from src.utils.auth import require_roles
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated


def get_user_data_service(db: AsyncSession = Depends(get_db)) -> UserData:
    return UserData(db)


user_data_router = APIRouter(
    tags=["User Data"],
    prefix="/user_data"
)


@user_data_router.get("/get_user_data_by_id/{user_id}")
async def get_user_data(
    user_id: int,
    _: Annotated[User, Depends(require_roles(["admin"]))],
    service: Annotated[UserData, Depends(get_user_data_service)]
):
    return await service.get_user_data_by_id(user_id=user_id)


@user_data_router.get("/get_user_data_by_passport_data_filter")
async def get_user_data_by_passport_data_filter(
    _: Annotated[User, Depends(require_roles(["admin"]))],
    service: Annotated[UserData, Depends(get_user_data_service)],
    passport_series_number: str | None = Query(None),
    jshshir: str | None = Query(None),
    first_name: str | None = Query(None),
    last_name: str | None = Query(None),
    third_name: str | None = Query(None),
    region: str | None = Query(None),
    gender: str | None = Query(None),
    limit: int = Query(10, ge=1),
    offset: int = Query(0, ge=0),
):
    filter_field = UserDataFilterByPassportData(
        passport_series_number=passport_series_number,
        jshshir=jshshir,
        first_name=first_name,
        last_name=last_name,
        third_name=third_name,
        region=region,
        gender=gender,
    )
    return await service.get_all_user_data_by_passport_data(
        filter_filed=filter_field,
        limit=limit,
        offset=offset
    )


@user_data_router.get("/get_user_data_by_study_info_filter")
async def get_user_data_by_study_info_filter(
    _: Annotated[User, Depends(require_roles(["admin"]))],
    service: Annotated[UserData, Depends(get_user_data_service)],
    study_form: str | None = Query(None),
    study_language: str | None = Query(None),
    study_direction_name: str | None = Query(None),
    education_type: str | None = Query(None),
    study_type: str | None = Query(None),
    limit: int = Query(10, ge=1),
    offset: int = Query(0, ge=0),
):
    filter_field = UserDataFilterByStudyInfo(
        study_form=study_form,
        study_language=study_language,
        study_direction_name=study_direction_name,
        education_type=education_type,
        study_type=study_type,
    )
    return await service.get_all_user_data_by_study_info(
        filter_field=filter_field,
        limit=limit,
        offset=offset
    )


@user_data_router.get("/users_with_study_info")
async def count_users_with_study_info(
    _: Annotated[User, Depends(require_roles(["admin"]))],
    service: Annotated[UserData, Depends(get_user_data_service)],
):
    return await service.count_all_users_with_related_data()

