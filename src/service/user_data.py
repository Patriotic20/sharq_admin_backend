from sqlalchemy.ext.asyncio import AsyncSession
from sharq_models.models import ( # type: ignore
    User, 
    StudyInfo, 
    PassportData,
    StudyLanguage,
    StudyForm,
    StudyDirection,
    StudyType,
    EducationType,
    
)
from src.service.study_info import StudyInfoCrud
from src.schemas.passport_data import PassportDataResponse
from src.schemas.study_info import StudyInfoResponse 
from src.schemas.user_data import UserDataResponse , UserDataFilterByPassportData , UserDataFilterByStudyInfo
from src.service import BasicCrud
from fastapi import HTTPException
from sqlalchemy import select , and_
from sqlalchemy.orm import joinedload


class UserData(BasicCrud):
    def __init__(self, db: AsyncSession):
        super().__init__(db)
        self.db = db
        self.study_info_service = StudyInfoCrud(db)

    async def get_user_data_by_id(self, user_id: int):
        stmt = select(User).where(User.id == user_id).options(
            joinedload(User.passport_data)
        )
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(status_code=404, detail="Foydalanuvchi topilmadi")

        study_info_stmt = select(StudyInfo).where(StudyInfo.user_id == user_id)
        study_info_result = await self.db.execute(study_info_stmt)
        study_info = study_info_result.scalar_one_or_none()

        study_info_response = (
            await self.study_info_service.get_study_info_by_id(study_info.id)
            if study_info else None
        )

        # serialize both fields to Pydantic response models
        passport_data_response = PassportDataResponse.model_validate(user.passport_data)
        study_info_response = (
            StudyInfoResponse.model_validate(study_info) if study_info else None
        )

        return UserDataResponse(
            passport_data=passport_data_response,
            study_info_data=study_info_response
        )
        
    async def get_all_user_data_by_passport_data(
        self,
        filter_filed: UserDataFilterByPassportData
    ) -> list[PassportData]:
        stmt = select(PassportData).options(
            joinedload(PassportData.user)
            .joinedload(User.study_info)
            .joinedload(StudyInfo.study_language),
            joinedload(PassportData.user)
            .joinedload(User.study_info)
            .joinedload(StudyInfo.study_form),
            joinedload(PassportData.user)
            .joinedload(User.study_info)
            .joinedload(StudyInfo.study_direction),
            joinedload(PassportData.user)
            .joinedload(User.study_info)
            .joinedload(StudyInfo.study_type),
            joinedload(PassportData.user)
            .joinedload(User.study_info)
            .joinedload(StudyInfo.education_type)
        )

        filters = []

        if filter_filed.passport_series_number:
            filters.append(PassportData.passport_series_number == filter_filed.passport_series_number)
        if filter_filed.jshshir:
            filters.append(PassportData.jshshir == filter_filed.jshshir)
        if filter_filed.first_name:
            filters.append(PassportData.first_name.ilike(f"%{filter_filed.first_name}%"))
        if filter_filed.last_name:
            filters.append(PassportData.last_name.ilike(f"%{filter_filed.last_name}%"))
        if filter_filed.third_name:
            filters.append(PassportData.third_name.ilike(f"%{filter_filed.third_name}%"))
        if filter_filed.region:
            filters.append(PassportData.region.ilike(f"%{filter_filed.region}%"))
        if filter_filed.gender:
            filters.append(PassportData.gender == filter_filed.gender)

        if filters:
            stmt = stmt.where(and_(*filters))

        result = await self.db.execute(stmt)
        return result.scalars().all()

            
    async def get_all_user_data_by_study_info(
        self,
        filter_field: UserDataFilterByStudyInfo
    ) -> list[User]:
        stmt = (
            select(User)
            .join(User.study_info)
            .join(StudyInfo.study_language)
            .join(StudyInfo.study_form)
            .join(StudyInfo.study_direction)
            .join(StudyInfo.study_type)
            .join(StudyInfo.education_type)
            .options(
                joinedload(User.passport_data),  
                joinedload(User.study_info)
                    .joinedload(StudyInfo.study_language),
                joinedload(User.study_info)
                    .joinedload(StudyInfo.study_form),
                joinedload(User.study_info)
                    .joinedload(StudyInfo.study_direction),
                joinedload(User.study_info)
                    .joinedload(StudyInfo.study_type),
                joinedload(User.study_info)
                    .joinedload(StudyInfo.education_type)
            )
        )

        filters = []

        if filter_field.study_language:
            filters.append(StudyLanguage.name == filter_field.study_language)
        if filter_field.study_form:
            filters.append(StudyForm.name == filter_field.study_form)
        if filter_field.study_direction_name:
            filters.append(StudyDirection.name.ilike(f"%{filter_field.study_direction_name}%"))
        if filter_field.study_type:
            filters.append(StudyType.name == filter_field.study_type)
        if filter_field.education_type:
            filters.append(EducationType.name == filter_field.education_type)

        if filters:
            stmt = stmt.where(and_(*filters))

        result = await self.db.execute(stmt)
        return result.scalars().all()


