from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select 
from sqlalchemy.orm import joinedload 

from sharq_models.models import StudyInfo  # type: ignore
from src.schemas.study_info import StudyInfoBase, StudyInfoResponse
from src.schemas.study_language import StudyLanguageResponse
from src.schemas.study_type import StudyTypeResponse
from src.schemas.education_type import EducationTypeResponse
from src.schemas.study_form import StudyFormResponse
from src.schemas.study_direction import StudyDirectionResponse
from src.service import BasicCrud


class StudyInfoCrud(BasicCrud[StudyInfo, StudyInfoBase]):
    def __init__(self, db: AsyncSession):
        super().__init__(db)

    async def _get_with_join(self, study_info_id: int) -> StudyInfoResponse:
        stmt = (
            select(StudyInfo)
            .options(
                joinedload(StudyInfo.study_language),
                joinedload(StudyInfo.study_form),
                joinedload(StudyInfo.study_direction),
                joinedload(StudyInfo.education_type),
                joinedload(StudyInfo.study_type)
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
            study_language=StudyLanguageResponse.model_validate(
                study_info.study_language, from_attributes=True
            ),
            study_form=StudyFormResponse.model_validate(
                study_info.study_form, from_attributes=True
            ),
            study_direction=StudyDirectionResponse.model_validate(
                study_info.study_direction, from_attributes=True
            ),
            education_type=EducationTypeResponse.model_validate(
                study_info.education_type, from_attributes=True
            ),
            study_type=StudyTypeResponse.model_validate(
                study_info.study_type, from_attributes=True
            ),
            graduate_year=study_info.graduate_year,
            certificate_path=study_info.certificate_path,
            dtm_sheet=study_info.dtm_sheet,
        )

    async def get_study_info_by_id(self, study_info_id: int) -> StudyInfoResponse:
        """
        Get a single StudyInfo with all nested relations by ID.
        """
        return await self._get_with_join(study_info_id=study_info_id)

    async def get_all_study_info(
        self, limit: int = 100, offset: int = 0
    ) -> list[StudyInfoResponse]:
        """
        Get all StudyInfo entries with nested relations.
        """
        stmt = (
            select(StudyInfo)
            .options(
                joinedload(StudyInfo.study_language),
                joinedload(StudyInfo.study_form),
                joinedload(StudyInfo.study_direction),
                joinedload(StudyInfo.education_type),
                joinedload(StudyInfo.study_type)
            )
            .limit(limit)
            .offset(offset)
        )
        result = await self.db.execute(stmt)
        study_infos = result.scalars().all()

        return [self._to_response_with_names(info) for info in study_infos]
    

