import os
import random
from io import BytesIO
from uuid import uuid4

import qrcode
from fastapi import HTTPException
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from weasyprint import HTML

from sharq_models.models import Contract, User, StudyInfo  # type: ignore
from src.service import BasicCrud

templates = Jinja2Templates(directory="src/templates")


class ReportService(BasicCrud):
    def __init__(self, db: AsyncSession):
        super().__init__(db=db)

    async def get_contract_by_id(self, user_id: int) -> Contract:
        contract = await super().get_by_field(Contract, "user_id", user_id)
        if not contract:
            raise HTTPException(status_code=404, detail="Contract not found")
        return contract

    def generate_temp_file_path(self, base_dir: str, extension: str) -> str:
        os.makedirs(base_dir, exist_ok=True)
        return os.path.join(base_dir, f"{uuid4().hex}{extension}")

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

    async def download_pdf(self, user_id: int) -> BytesIO:
        contract = await self.get_contract_by_id(user_id)

        if not contract.file_path:
            raise HTTPException(status_code=400, detail="File path not found in contract")

        html = await self.add_qr_code_in_report(user_id)
        pdf = BytesIO()
        HTML(string=html, base_url=".").write_pdf(pdf)
        pdf.seek(0)

        # Write to file_path (assumed from DB)
        os.makedirs(os.path.dirname(contract.file_path), exist_ok=True)
        with open(contract.file_path, "wb") as f:
            f.write(pdf.read())
        pdf.seek(0)

        return pdf

    async def download_3_pdf(self, user_id: int) -> BytesIO:
        html = await self.add_qr_code_in_report(user_id, is_three=True)
        pdf = BytesIO()
        HTML(string=html, base_url=".").write_pdf(pdf)
        pdf.seek(0)
        return pdf

    async def add_qr_code_in_report(self, user_id: int, is_three: bool = False) -> str:
        contract = await self.get_contract_by_id(user_id)
        if not contract.file_path:
            raise HTTPException(status_code=400, detail="File path not found in contract")

        qr_path = self.generate_temp_file_path("uploads/media/qr_codes", ".png")
        file_url = f"http://localhost:8082/{contract.file_path}"
        self.generate_qr_code(data=file_url, save_path=qr_path)

        template_name = "uchtomon.html" if is_three else "ikki.html"
        return await self.generate_report(user_id, template_name, qr_path)

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
