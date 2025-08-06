from fastapi import HTTPException, status
from src.service import BasicCrud
from sharq_models.models import EducationType #type: ignore 
from src.schemas.education_type import (
    EducationTypeBase,
    EducationTypeUpdate,
    EducationTypeFilter,
    EducationTypeResponse,
)
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List


class EducationTypeCrud(BasicCrud[EducationType, EducationTypeBase]):
    def __init__(self, db: AsyncSession):
        super().__init__(db)

    async def create_education_type(
        self, obj: EducationTypeBase
    ) -> EducationTypeResponse:
        existing = await super().get_by_field(
            model=EducationType,
            field_name="name",
            field_value=obj.name,
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Bunday o'qish turi allaqachon mavjud",
            )

        return await super().create(model=EducationType, obj_items=obj)

    async def get_by_education_type_id(self, education_id: int) -> EducationTypeResponse:
        education_type = await super().get_by_id(
            model=EducationType, item_id=education_id
        )

        if not education_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="O'qish turi topilmadi"
            )

        return education_type

    async def get_education_type_all(
        self, filter_obj: EducationTypeFilter, limit: int = 100, offset: int = 0
    ) -> List[EducationTypeResponse]:
        filters = []

        if filter_obj.name:
            filters.append(EducationType.name.ilike(f"%{filter_obj.name}%"))

        return await super().get_all(
            model=EducationType, limit=limit, offset=offset, filters=filters or None
        )

    async def update_education_type(
        self, education_id: int, obj: EducationTypeUpdate
    ) -> EducationTypeResponse:
        await self.get_by_education_type_id(education_id)
        return await super().update(
            model=EducationType, item_id=education_id, obj_items=obj
        )

    async def delete_education_type(self, education_id: int) -> dict:
        await self.get_by_education_type_id(education_id)
        return await super().delete(model=EducationType, item_id=education_id)
