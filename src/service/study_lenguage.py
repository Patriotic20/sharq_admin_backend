from fastapi import HTTPException, status
from src.service import BasicCrud
from sharq_models.models import StudyLanguage #type: ignore 
from src.schemas.study_language import (
    StudyLanguageBase,
    StudyLanguageUpdate,
    StudyLanguageFilter,
    StudyLanguageResponse,
)
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List


class StudyLanguageCrud(BasicCrud[StudyLanguage, StudyLanguageBase]):
    def __init__(self, db: AsyncSession):
        super().__init__(db)

    async def create_study_language(
        self, obj: StudyLanguageBase
    ) -> StudyLanguageResponse:
        existing = await super().get_by_field(
            model=StudyLanguage,
            field_name="name",
            field_value=obj.name,
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Bunday til allaqachon mavjud",
            )

        return await super().create(model=StudyLanguage, obj_items=obj)

    async def get_by_study_language_id(self, language_id: int) -> StudyLanguageResponse:
        study_language = await super().get_by_id(
            model=StudyLanguage, item_id=language_id
        )

        if not study_language:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Til topilmadi"
            )

        return study_language

    async def get_study_language_all(
        self, filter_obj: StudyLanguageFilter, limit: int = 100, offset: int = 0
    ) -> List[StudyLanguageResponse]:
        filters = []

        if filter_obj.name:
            filters.append(StudyLanguage.name.ilike(f"%{filter_obj.name}%"))

        return await super().get_all(
            model=StudyLanguage, limit=limit, offset=offset, filters=filters or None
        )

    async def update_study_language(
        self, language_id: int, obj: StudyLanguageUpdate
    ) -> StudyLanguageResponse:
        await self.get_by_study_language_id(language_id)
        return await super().update(
            model=StudyLanguage, item_id=language_id, obj_items=obj
        )

    async def delete_study_language(self, language_id: int) -> dict:
        await self.get_by_study_language_id(language_id)
        return await super().delete(model=StudyLanguage, item_id=language_id)
