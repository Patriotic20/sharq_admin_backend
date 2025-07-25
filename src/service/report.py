import os
import random
from io import BytesIO
from uuid import uuid4

from urllib.parse import urlparse

import qrcode
from fastapi import HTTPException
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from src.schemas.contract import ContractCreate
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from weasyprint import HTML

from sharq_models.models import Contract, User, StudyInfo  # type: ignore
from src.service import BasicCrud
from src.core.config import settings

templates = Jinja2Templates(directory="src/templates")


class ReportService(BasicCrud):
    def __init__(self, db: AsyncSession):
        super().__init__(db=db)
        self.contract_dir_url = f"{settings.base_url}/uploads/contract"
        self.contract_dir_path = "uploads/contract"
        self.contract_two_side = f"{self.contract_dir_url}/two_side"
        self.contract_three_side = f"{self.contract_dir_url}/three_side"
        self.qr_code_dir_path = "uploads/qr_codes"

    async def get_contract_by_user_id(self, user_id: int):
        return await super().get_by_field(model=Contract, field_name="user_id", field_value=user_id)

    def generate_qr_code(self, data: str, save_path: str) -> None:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        img = qr.make_image(fill="black", back_color="white")
        img.save(save_path)

    def generate_file_path(self, base_dir: str, extension: str) -> str:
        filename = f"{uuid4().hex}{extension}"
        full_path = os.path.join(base_dir, filename)
        return full_path
    
    
    async def create_and_add_file_path(self, base_dir: str, extension: str, user_id: int) -> Contract:
        filename = f"{uuid4().hex}{extension}"
        full_path = os.path.join(base_dir, filename)
        
        contract_data = ContractCreate(
            user_id=user_id,
            file_path=full_path,
            status=True,
        )
        return await super().create(model=Contract , obj_items=contract_data)
        
        

    async def _get_contract_data(self, user_id: int) -> Contract:
        stmt = (
            select(Contract)
            .options(
                joinedload(Contract.user).joinedload(User.passport_data),
                joinedload(Contract.user).joinedload(User.study_info).joinedload(StudyInfo.study_form),
                joinedload(Contract.user).joinedload(User.study_info).joinedload(StudyInfo.study_type),
                joinedload(Contract.user).joinedload(User.study_info).joinedload(StudyInfo.study_direction),
            )
            .where(Contract.user_id == user_id)
        )
        result = await self.db.execute(stmt)
        contract = result.scalars().first()

        if not contract:
            raise HTTPException(status_code=404, detail="Contract not found")
        
        if not contract.user.study_info:
            raise HTTPException(status_code=404, detail="Study info not found for this user")
        
        return contract

    def _get_full_name(self, passport) -> str:
        return " ".join(filter(None, [passport.last_name, passport.first_name, passport.third_name]))

    def _generate_contract_id(self) -> str:
        return str(random.randint(0, 999999)).zfill(6)

    async def generate_report(self, user_id: int, template_name: str, edu_course_level: int ,qr_code_path: str | None = None ) -> str:
        contract = await self._get_contract_data(user_id)
        user = contract.user
        passport = user.passport_data
        study_info = user.study_info
        direction = study_info.study_direction if study_info else None

        if not (passport and study_info and direction):
            raise HTTPException(status_code=400, detail="Required user info is missing")
        print(f"<<<<<<<<<<<<<<<<<<unitl context edu_course_level {edu_course_level}")

        context = {
            "contract_id": self._generate_contract_id(),
            "fio": self._get_full_name(passport),
            "edu_course_level": f"{edu_course_level}-kurs",
            "edu_form": study_info.study_form.name if study_info.study_form else "",
            "edu_type": study_info.study_type.name if study_info.study_type else "",
            "edu_year": direction.education_years,
            "edu_direction": direction.name,
            "contract_price": direction.contract_sum,
            "address": passport.address or "",
            "passport_id": passport.passport_series_number or "",
            "jshir": passport.jshshir or "",
            "phone_number": user.phone_number or "",
            "qr_code_path": qr_code_path,
        }
        
        print(f"<<<<<<<<<<<<<<<<<<after context edu_course_level {context.get(edu_course_level)}")
        return templates.get_template(template_name).render(context)

    async def add_qr_code_in_report(self, user_id: int,  edu_course_level: int ,is_three: bool = False) -> str:
        contract = await self.get_contract_by_user_id(user_id=user_id)
        if not contract or not contract.file_path:
            raise HTTPException(status_code=404, detail="Contract not found or file path missing")

        qr_path = self.generate_file_path(self.qr_code_dir_path, ".png")
        self.generate_qr_code(data=contract.file_path, save_path=qr_path)

        template_name = "uchtomon.html" if is_three else "ikki.html"
        return await self.generate_report(user_id=user_id, template_name=template_name, qr_code_path=qr_path , edu_course_level=edu_course_level)

    async def report_2_download_pdf(self, user_id: int, edu_course_level: int ,is_three: bool = False) -> str:
        contract = await self.get_contract_by_user_id(user_id=user_id)
        print("<<<<<<<<<<<<<<<<<<<<<Get contract by user id>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
        if contract and contract.file_path and "two_side" in contract.file_path:
            file_url = contract.file_path
            print(f"<<<<<<<<<<<<<<<<<<<<<Get contract by user id {file_url}>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
            parsed_url = urlparse(file_url)
            print(f"<<<<<<<<<<<<<<<Parse url : {parsed_url}")
            return parsed_url.path.lstrip("/")
        else:
            contract = await self.create_and_add_file_path(
                base_dir=self.contract_two_side,
                extension=".pdf",
                user_id=user_id,
            )
            file_url = contract.file_path
            print(f"<<<<<<<<<<<<<<<create_and_add_file_path url : {file_url}")
            html_content = await self.add_qr_code_in_report(user_id=user_id, is_three=is_three , edu_course_level=edu_course_level)
            print(f"<<<<<<<<<<<<<<<<<<edu_course_level {edu_course_level}")
            print("<<<<<<<<<<<<<<<add_qr_code_in_report>>>>>>>>>>>>>>>>>>>>>>>")
            
            pdf = BytesIO()
            HTML(string=html_content, base_url=".").write_pdf(pdf)
            pdf.seek(0)
            parsed_url = urlparse(file_url)
            file_path = parsed_url.path.lstrip("/")
            print(f"<<<<<<<<<<<<<<<<<<< file path: {file_path}")

            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "wb") as f:
                f.write(pdf.read())
            pdf.seek(0)
            print("<<<<<<<<<<<<<<<<<<<<<<<Saved in uploads contract two side folder>>>>>>>>>>>>>>>>>>>>>>>")
            
            parsed_url = urlparse(file_url)
            return parsed_url.path.lstrip("/")
        
    async def report_3_download_pdf(self, user_id: int, edu_course_level: int ,is_three: bool = True ) -> str:
        contract = await self.get_contract_by_user_id(user_id=user_id)
        print("<<<<<<<<<<<<<<<<<<<<<Get contract by user id>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
        if contract and contract.file_path and "three_side" in contract.file_path:
            file_url = contract.file_path
            parsed_url = urlparse(file_url)
            print(f"<<<<<<<<<<<<<<<Parse url : {parsed_url}")
            return parsed_url.path.lstrip("/")
        else:
            contract = await self.create_and_add_file_path(
                base_dir=self.contract_three_side,
                extension=".pdf",
                user_id=user_id,
            )
            file_url = contract.file_path
            print(f"<<<<<<<<<<<<<<<create_and_add_file_path url : {file_url}")

            html_content = await self.add_qr_code_in_report(user_id=user_id, is_three=is_three , edu_course_level=edu_course_level)
            print("<<<<<<<<<<<<<<<add_qr_code_in_report>>>>>>>>>>>>>>>>>>>>>>>")
            
            pdf = BytesIO()
            HTML(string=html_content, base_url=".").write_pdf(pdf)
            pdf.seek(0)
            parsed_url = urlparse(file_url)
            file_path = parsed_url.path.lstrip("/")
            print(f"<<<<<<<<<<<<<<<<<<< file path: {file_path}")

            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "wb") as f:
                f.write(pdf.read())
            pdf.seek(0)
            print("<<<<<<<<<<<<<<<<<<<<<<<Saved in uploads contract three side folder>>>>>>>>>>>>>>>>>>>>>>>")
            parsed_url = urlparse(file_url)
            return parsed_url.path.lstrip("/")
        
        
        
    async def generate_both_report(self, user_id: int, edu_course_level: int):
        await self.report_2_download_pdf(user_id=user_id , edu_course_level=edu_course_level, is_three=False)
        print("<<<<<<<<<<<<<<<<<<<<<Report 2 download pdf >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
        await self.report_3_download_pdf(user_id=user_id , edu_course_level=edu_course_level, is_three=True)
        print("<<<<<<<<<<<<<<<<<<<<<Report 3 download pdf >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
        
        
    async def get_all_reports_by_id(self, user_id: int):
        stmt = select(Contract).where(Contract.user_id == user_id)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_two_side_report(self, user_id: int):
        contract_list = await self.get_all_reports_by_id(user_id=user_id)
        for contract in contract_list:
            if "two_side" in contract.file_path:
                parsed_url = urlparse(contract.file_path)
                return parsed_url.path.lstrip("/")
        return None  

    async def get_three_side_report(self, user_id: int):
        contract_list = await self.get_all_reports_by_id(user_id=user_id)
        for contract in contract_list:
            if "three_side" in contract.file_path:
                parsed_url = urlparse(contract.file_path)
                return parsed_url.path.lstrip("/")
        return None
    
    async def get_all_reposrts(self):
        stmt = select(Contract)
        result = await self.db.execute(stmt)
        return result.scalars().all()
        
        
        
