import asyncio
from fastapi import HTTPException
from sharq_models.models import User , PassportData , StudyLanguage , StudyForm , StudyDirection , StudyType , EducationType # type: ignore
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func , and_
from sqlalchemy.orm import joinedload 




from sharq_models.models import StudyInfo, Contract  # type: ignore
from src.schemas.study_info import StudyInfoBase, StudyInfoResponse, StudyInfoCreate , StudyInfoListResponse
from src.schemas.study_language import StudyLanguageResponse
from src.schemas.study_type import StudyTypeResponse
from src.schemas.education_type import EducationTypeResponse
from src.schemas.study_form import StudyFormResponse
from src.schemas.study_direction import StudyDirectionResponse
from src.schemas.passport_data import PassportDataResponse
from src.service import BasicCrud
from src.schemas.user_data import UserDataFilterByPassportData , UserDataFilterByStudyInfo


class StudyInfoCrud(BasicCrud[StudyInfo, StudyInfoBase]):
    def __init__(self, db: AsyncSession):
        super().__init__(db)

    async def _get_with_join(self, study_info_id: int) -> StudyInfoResponse:
        try:
            stmt = (
                select(StudyInfo)
                .options(
                    joinedload(StudyInfo.study_language),
                    joinedload(StudyInfo.study_form),
                    joinedload(StudyInfo.study_direction),
                    joinedload(StudyInfo.education_type),
                    joinedload(StudyInfo.study_type),
                    joinedload(StudyInfo.user).joinedload(User.passport_data)
                )
                .where(StudyInfo.id == study_info_id)
            )
            result = await self.db.execute(stmt)
            study_info = result.scalar_one_or_none()

            if not study_info:
                raise HTTPException(status_code=404, detail="Ma'lumot topilmadi")

            return await self._to_response_with_names(study_info)
        except Exception as e:
            await self.db.rollback()
            raise e

    async def _to_response_with_names(self, study_info: StudyInfo) -> StudyInfoResponse:
        contract_paths = await self._get_contract_paths(study_info.user_id)
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
            passport_data=PassportDataResponse.model_validate(
                study_info.user.passport_data, from_attributes=True
            ),
            phone_number=study_info.user.phone_number,
            graduate_year=study_info.graduate_year,
            certificate_path=study_info.certificate_path,
            dtm_sheet=study_info.dtm_sheet,
            contract_paths=contract_paths,
            is_approved=len(contract_paths) > 0,
        )

    async def _to_response_with_names_optimized(self, study_info: StudyInfo) -> StudyInfoResponse:
        # Use already loaded contracts instead of making another query
        contract_paths = [contract.file_path for contract in study_info.user.contracts]
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
            passport_data=PassportDataResponse.model_validate(
                study_info.user.passport_data, from_attributes=True
            ),
            graduate_year=study_info.graduate_year,
            certificate_path=study_info.certificate_path,
            dtm_sheet=study_info.dtm_sheet,
            contract_paths=contract_paths,
            is_approved=len(contract_paths) > 0,
        )

    async def get_study_info_by_id(self, study_info_id: int) -> StudyInfoResponse:
        """
        Get a single StudyInfo with all nested relations by ID.
        """
        return await self._get_with_join(study_info_id=study_info_id)

    async def get_all_study_info(
        self,
        passport_filter: UserDataFilterByPassportData = None,
        study_info_filter: UserDataFilterByStudyInfo = None,
        limit: int = 100,
        offset: int = 0
    ) ->  StudyInfoListResponse:
        """
        Get all StudyInfo entries with nested relations and optional filters.
        """
        stmt = (
            select(StudyInfo).distinct()
            # .join(StudyInfo.user)
            # .join(User.passport_data)
            # .join(StudyInfo.study_language)
            # .join(StudyInfo.study_form)
            # .join(StudyInfo.study_direction)
            # .join(StudyInfo.study_type)
            # .join(StudyInfo.education_type)
            .options(
                joinedload(StudyInfo.study_language),
                joinedload(StudyInfo.study_form),
                joinedload(StudyInfo.study_direction),
                joinedload(StudyInfo.education_type),
                joinedload(StudyInfo.study_type),
                joinedload(StudyInfo.user).joinedload(User.passport_data),
            )
            .order_by(StudyInfo.id.desc())
            .limit(limit)
            .offset(offset)
        )

        filters = []

        # Passport filters
        if passport_filter:
            if passport_filter.passport_series_number:
                filters.append(PassportData.passport_series_number == passport_filter.passport_series_number)
            if passport_filter.jshshir:
                filters.append(PassportData.jshshir == passport_filter.jshshir)
            if passport_filter.first_name:
                filters.append(PassportData.first_name.ilike(f"%{passport_filter.first_name}%"))
            if passport_filter.last_name:
                filters.append(PassportData.last_name.ilike(f"%{passport_filter.last_name}%"))
            if passport_filter.third_name:
                filters.append(PassportData.third_name.ilike(f"%{passport_filter.third_name}%"))
            if passport_filter.region:
                filters.append(PassportData.region.ilike(f"%{passport_filter.region}%"))
            if passport_filter.gender:
                filters.append(PassportData.gender == passport_filter.gender)

        # StudyInfo filters
        if study_info_filter:
            if study_info_filter.study_language:
                filters.append(StudyLanguage.name == study_info_filter.study_language)
            if study_info_filter.study_form:
                filters.append(StudyForm.name == study_info_filter.study_form)
            if study_info_filter.study_direction_name:
                filters.append(StudyDirection.name.ilike(f"%{study_info_filter.study_direction_name}%"))
            if study_info_filter.study_type:
                filters.append(StudyType.name == study_info_filter.study_type)
            if study_info_filter.education_type:
                filters.append(EducationType.name == study_info_filter.education_type)

        # Apply filters
        if filters:
            stmt = stmt.where(and_(*filters))

        # Execute main query
        result = await self.db.execute(stmt)
        study_infos = result.scalars().all()

        # Get total count (filtered)
        count_stmt = select(func.count(StudyInfo.id))
        if filters:
            count_stmt = count_stmt.join(StudyInfo.user).join(User.passport_data)
            count_stmt = count_stmt.where(and_(*filters))
        total_result = await self.db.execute(count_stmt)
        total = total_result.scalar_one()

        # Build response objects
        responses = []
        for info in study_infos:
            response = await self._to_response_with_names(info)
            responses.append(response)

        return {"data": responses, "total": total}
            
    async def create_study_info(self, study_info_data: StudyInfoCreate) -> StudyInfoResponse:
        existing_study_info = await self.get_by_field(model=StudyInfo, field_name="user_id", field_value=study_info_data.user_id)
        if existing_study_info:
            raise HTTPException(status_code=400, detail="Study info already exists")
        return await super().create(model=StudyInfo, obj_items=study_info_data)
        
    
    async def _get_contract_paths(self, user_id: int) -> list[str]:
        stmt = (
            select(Contract)
            .where(Contract.user_id == user_id)
        )
        result = await self.db.execute(stmt)
        contracts = result.scalars().all()
        return [contract.file_path for contract in contracts]




