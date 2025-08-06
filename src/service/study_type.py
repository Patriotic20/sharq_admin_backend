from fastapi import HTTPException, status
from src.service import BasicCrud
from sharq_models.models import StudyType #type: ignore 
from src.schemas.study_type import (
    StudyTypeBase,
    StudyTypeUpdate,
    StudyTypeFilter,
    StudyTypeResponse,
)
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List


class StudyTypeCrud(BasicCrud[StudyType, StudyTypeBase]):
    def __init__(self, db: AsyncSession):
        super().__init__(db)

    async def create_study_type(
        self, obj: StudyTypeBase
    ) -> StudyTypeResponse:
        existing = await super().get_by_field(
            model=StudyType,
            field_name="name",
            field_value=obj.name,
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Bunday o'qish turi allaqachon mavjud",
            )

        return await super().create(model=StudyType, obj_items=obj)

    async def get_by_study_type_id(self, study_id: int) -> StudyTypeResponse:
        study_type = await super().get_by_id(
            model=StudyType, item_id=study_id
        )

        if not study_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="O'qish turi topilmadi"
            )

        return study_type

    async def get_study_type_all(
        self, filter_obj: StudyTypeFilter, limit: int = 100, offset: int = 0
    ) -> List[StudyTypeResponse]:
        filters = []

        if filter_obj.name:
            filters.append(StudyType.name.ilike(f"%{filter_obj.name}%"))

        return await super().get_all(
            model=StudyType, limit=limit, offset=offset, filters=filters or None
        )

    async def update_study_type(
        self, study_id: int, obj: StudyTypeUpdate
    ) -> StudyTypeResponse:
        await self.get_by_study_type_id(study_id)
        return await super().update(
            model=StudyType, item_id=study_id, obj_items=obj
        )

    async def delete_study_type(self, study_id: int) -> dict:
        await self.get_by_study_type_id(study_id)
        return await super().delete(model=StudyType, item_id=study_id)
