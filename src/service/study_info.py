import asyncio
from fastapi import HTTPException
from sharq_models.models import User , PassportData , StudyLanguage , StudyForm , StudyDirection , StudyType , EducationType # type: ignore
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func , and_ , or_ , delete
from sqlalchemy.orm import joinedload  , selectinload
import openpyxl
import io


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
            passport_data=(
                PassportDataResponse.model_validate(study_info.user.passport_data, from_attributes=True)
                if study_info.user and study_info.user.passport_data
                else None
            ),
            phone_number=study_info.user.phone_number if study_info.user else None,
            graduate_year=study_info.graduate_year,
            certificate_path=study_info.certificate_path,
            dtm_sheet=study_info.dtm_sheet,
            contract_paths=contract_paths,
            is_approved=len(contract_paths) > 0,
            create_at=study_info.create_at
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
    search: str | None = None,  # <-- added search parameter
    limit: int = 100,
    offset: int = 0
        ) -> StudyInfoListResponse:

        stmt = (
            select(StudyInfo)
            .options(
                selectinload(StudyInfo.user).selectinload(User.contracts),
                selectinload(StudyInfo.user).selectinload(User.passport_data),
                selectinload(StudyInfo.study_language),
                selectinload(StudyInfo.study_form),
                selectinload(StudyInfo.study_direction),
                selectinload(StudyInfo.education_type),
                selectinload(StudyInfo.study_type),
            )
            .order_by(StudyInfo.id.desc())
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

        # Search filter
        if search:
            search_term = f"%{search}%"
            filters.append(
                or_(
                    PassportData.first_name.ilike(search_term),
                    PassportData.last_name.ilike(search_term),
                    PassportData.third_name.ilike(search_term),
                    PassportData.passport_series_number.ilike(search_term),
                    PassportData.jshshir.ilike(search_term),
                    StudyDirection.name.ilike(search_term),
                    StudyLanguage.name.ilike(search_term),
                )
            )

        # Apply joins only if there are filters
        if filters:
            stmt = stmt.join(StudyInfo.user).join(User.passport_data)
            stmt = stmt.join(StudyInfo.study_language).join(StudyInfo.study_form)
            stmt = stmt.join(StudyInfo.study_direction).join(StudyInfo.study_type).join(StudyInfo.education_type)
            stmt = stmt.where(and_(*filters))

        stmt = stmt.limit(limit).offset(offset)

        result = await self.db.execute(stmt)
        study_infos = result.scalars().all()

        responses = [await self._to_response_with_names(info) for info in study_infos]

        # Count
        count_stmt = select(func.count(StudyInfo.id))
        if filters:
            count_stmt = count_stmt.join(StudyInfo.user).join(User.passport_data)
            count_stmt = count_stmt.join(StudyInfo.study_language).join(StudyInfo.study_form)
            count_stmt = count_stmt.join(StudyInfo.study_direction).join(StudyInfo.study_type).join(StudyInfo.education_type)
            count_stmt = count_stmt.where(and_(*filters))
        total = (await self.db.execute(count_stmt)).scalar_one()

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




    async def export_to_excel(
            self,
            passport_filter: UserDataFilterByPassportData = None,
            study_info_filter: UserDataFilterByStudyInfo = None,
            search: str | None = None,
            limit: int = 1000,
            offset: int = 0,
        ) -> io.BytesIO:
            """
            Export StudyInfo data with relations to an Excel file.
            """
            result = await self.get_all_study_info(
                passport_filter=passport_filter,
                study_info_filter=study_info_filter,
                search=search,
                limit=limit,
                offset=offset,
            )

            study_infos = result["data"]

            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "StudyInfo"

            headers = [
                "ID",
                "User ID",
                "First Name",
                "Last Name",
                "Third Name",
                "Phone Number",
                "Passport Number",
                "JSHSHIR",
                "Is Approved",
                "Study Direction",
                "Study Form",
                "Study Type",
                "Study Language",
                "Education Type",
                "Graduate Year",
                "Certificate Path",
                "DTM Sheet",
                "Created At",
            ]
            ws.append(headers)

            for info in study_infos:
                passport = info.passport_data
                ws.append([
                    info.id,
                    info.user_id,
                    passport.first_name if passport else None,
                    passport.last_name if passport else None,
                    passport.third_name if passport else None,
                    info.phone_number,
                    passport.passport_series_number if passport else None,
                    passport.jshshir if passport else None,
                    info.is_approved,
                    info.study_direction.name if info.study_direction else None,
                    info.study_form.name if info.study_form else None,
                    info.study_type.name if info.study_type else None,
                    info.study_language.name if info.study_language else None,
                    info.education_type.name if info.education_type else None,
                    info.graduate_year,
                    info.certificate_path,
                    info.dtm_sheet,
                    info.create_at,
                ])

            stream = io.BytesIO()
            wb.save(stream)
            stream.seek(0)
            return stream

    async def delete_study_info(
            self,
            user_id: int | None = None,
            study_info_id: int | None = None,
        ) -> bool:
            """
            Delete StudyInfo by either study_info_id or user_id.
            Returns True if deleted, False if nothing was found.
            """
            if not user_id and not study_info_id:
                raise ValueError("Either user_id or study_info_id must be provided")

            query = select(StudyInfo)
            if study_info_id:
                query = query.where(StudyInfo.id == study_info_id)
            elif user_id:
                query = query.where(StudyInfo.user_id == user_id)

            result = await self.db.execute(query)
            study_info = result.scalar_one_or_none()

            if not study_info:
                return {
                    "delete": False,
                    "message": "StudyInfo not found"
                }

            await self.db.delete(study_info)
            await self.db.commit()
            return {
                "delete": True,
                "message": "Delete successfully"
            }
