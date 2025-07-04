from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from typing import List

from sharq_models.models import StudyInfo
from src.schemas.study_info import (
    StudyInfoBase,
    StudyInfoCreate,
    StudyInfoFilter,
    StudyInfoResponse,
)
from src.service import BasicCrud


class StudyInfoCrud(BasicCrud[StudyInfo, StudyInfoBase]):
    def __init__(self, db: AsyncSession):
        super().__init__(db)

    async def _create_study_info_if_not_exists(self, obj: StudyInfoCreate) -> StudyInfo:
        exist_user = await super().get_by_field(
            model=StudyInfo,
            field_name="user_id",
            field_value=obj.user_id
        )
        if exist_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Foydalanuvchiga tegishli ma'lumot allaqachon mavjud"
            )
        return await super().create(model=StudyInfo, obj_items=obj)

    async def _get_with_join(self, study_info_id: int) -> StudyInfoResponse:
        stmt = (
            select(StudyInfo)
            .options(
                joinedload(StudyInfo.study_language),
                joinedload(StudyInfo.study_form),
                joinedload(StudyInfo.study_direction),
            )
            .where(StudyInfo.id == study_info_id)
        )
        result = await self.db.execute(stmt)
        study_info = result.scalar_one_or_none()

        if not study_info:
            raise HTTPException(status_code=404, detail="Ma'lumot topilmadi")

        return self._to_response_with_names(study_info)

    def _to_response_with_names(self, study_info: StudyInfo) -> StudyInfoResponse:
        return StudyInfoResponse(
            id=study_info.id,
            user_id=study_info.user_id,
            study_language=study_info.study_language.name,
            study_form=study_info.study_form.name,
            study_direction=study_info.study_direction.name,
        )

    async def get_by_id_study_info(self, study_info_id: int) -> StudyInfoResponse:
        return await self._get_with_join(study_info_id=study_info_id)

    async def get_all_study_info(
        self,
        filters_data: StudyInfoFilter,
        limit: int = 100,
        offset: int = 0,
    ) -> List[StudyInfoResponse]:
        filters = []

        if filters_data.study_language:
            filters.append(StudyInfo.study_language_id == filters_data.study_language)
        if filters_data.study_form:
            filters.append(StudyInfo.study_form_id == filters_data.study_form)
        if filters_data.study_direction:
            filters.append(StudyInfo.study_direction_id == filters_data.study_direction)

        stmt = (
            select(StudyInfo)
            .options(
                joinedload(StudyInfo.study_language),
                joinedload(StudyInfo.study_form),
                joinedload(StudyInfo.study_direction),
            )
            .where(*filters)
            .limit(limit)
            .offset(offset)
        )

        result = await self.db.execute(stmt)
        study_infos = result.scalars().all()
        return [self._to_response_with_names(info) for info in study_infos]

    async def update_study_info(self, study_info_id: int, obj: StudyInfoBase):
        await self.get_by_id_study_info(study_info_id=study_info_id)
        await super().update(model=StudyInfo, item_id=study_info_id, obj_items=obj)
        return await self._get_with_join(study_info_id=study_info_id)

    async def delete_study_info(self, study_info_id: int):
        await self.get_by_id_study_info(study_info_id=study_info_id)
        return await super().delete(model=StudyInfo, item_id=study_info_id)
