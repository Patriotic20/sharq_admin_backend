from fastapi import HTTPException, status
from src.service import BasicCrud
from sharq_models.models import StudyForm #type: ignore
from src.schemas.study_form import (
    StudyFormBase,
    StudyFormUpdate,
    StudyFormFilter,
    StudyFormResponse,
)
from sqlalchemy.ext.asyncio import AsyncSession



class StudyFormCrud(BasicCrud[StudyForm, StudyFormBase]):
    def __init__(self, db: AsyncSession):
        super().__init__(db)

    async def create_study_form(self, obj: StudyFormBase) -> StudyFormResponse:
        existing = await super().get_by_field(
            model=StudyForm,
            field_name="name",
            field_value=obj.name,
        )

        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Bunday o'quv shakli allaqachon mavjud",
            )

        return await super().create(model=StudyForm, obj_items=obj)

    async def get_by_study_form_id(self, form_id: int) -> StudyFormResponse:
        study_form = await super().get_by_id(model=StudyForm, item_id=form_id)

        if not study_form:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="O'quv shakli topilmadi"
            )

        return study_form

    async def get_study_form_all(
        self, filter_obj: StudyFormFilter, limit: int = 100, offset: int = 0
    ) -> list[StudyFormResponse]:
        filters = []

        if filter_obj.name:
            filters.append(StudyForm.name.ilike(f"%{filter_obj.name}%"))

        return await super().get_all(
            model=StudyForm, limit=limit, offset=offset, filters=filters or None
        )

    async def update_study_form(
        self, form_id: int, obj: StudyFormUpdate
    ) -> StudyFormResponse:
        await self.get_by_study_form_id(form_id)
        return await super().update(model=StudyForm, item_id=form_id, obj_items=obj)

    async def delete_study_form(self, form_id: int) -> dict:
        await self.get_by_study_form_id(form_id)
        return await super().delete(model=StudyForm, item_id=form_id)
