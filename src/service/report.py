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
            edu_course_level=1
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
        return contract

    def _get_full_name(self, passport) -> str:
        return " ".join(filter(None, [passport.last_name, passport.first_name, passport.third_name]))

    def _generate_contract_id(self) -> str:
        return str(random.randint(0, 999999)).zfill(6)

    async def generate_report(self, user_id: int, template_name: str, qr_code_path: str | None = None) -> str:
        contract = await self._get_contract_data(user_id)
        user = contract.user
        passport = user.passport_data
        study_info = user.study_info
        direction = study_info.study_direction if study_info else None

        if not (passport and study_info and direction):
            raise HTTPException(status_code=400, detail="Required user info is missing")

        context = {
            "contract_id": self._generate_contract_id(),
            "fio": self._get_full_name(passport),
            "edu_course_level": f"{contract.edu_course_level}-kurs",
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
        return templates.get_template(template_name).render(context)

    async def add_qr_code_in_report(self, user_id: int, is_three: bool = False) -> str:
        contract = await self.get_contract_by_user_id(user_id=user_id)
        if not contract or not contract.file_path:
            raise HTTPException(status_code=404, detail="Contract not found or file path missing")

        qr_path = self.generate_file_path(self.qr_code_dir_path, ".png")
        self.generate_qr_code(data=contract.file_path, save_path=qr_path)

        template_name = "uchtomon.html" if is_three else "ikki.html"
        return await self.generate_report(user_id=user_id, template_name=template_name, qr_code_path=qr_path)

    async def download_pdf(self, user_id: int, is_three: bool = False) -> str:
        contract = await self.get_contract_by_user_id(user_id=user_id)

        if contract and contract.file_path:
            file_url = contract.file_path
        else:
            contract = await self.create_and_add_file_path(
                base_dir=self.contract_dir_url,
                extension=".pdf",
                user_id=user_id,
            )
            file_url = contract.file_path

            html_content = await self.add_qr_code_in_report(user_id=user_id, is_three=is_three)
            pdf = BytesIO()
            HTML(string=html_content, base_url=".").write_pdf(pdf)
            pdf.seek(0)

            parsed_url = urlparse(file_url)
            file_path = parsed_url.path.lstrip("/")

            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "wb") as f:
                f.write(pdf.read())
            pdf.seek(0)

        parsed_url = urlparse(file_url)
        return parsed_url.path.lstrip("/")

