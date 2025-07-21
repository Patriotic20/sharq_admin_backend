import random
import datetime
import os
from io import BytesIO
from uuid import uuid4

import qrcode
import qrcode.constants
from weasyprint import HTML
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import HTTPException

from src.schemas.contract import ContractCreate
from sharq_models.models import Contract, User, StudyInfo  # type: ignore
from src.service import BasicCrud

templates = Jinja2Templates(directory="src/templates")


class ReportService(BasicCrud):
    def __init__(self, db: AsyncSession):
        super().__init__(db=db)

    def generate_file_path(self, base_dir: str, extension: str) -> str:
        filename = f"{uuid4().hex}{extension}"
        full_path = os.path.join(base_dir, filename)
        os.makedirs(base_dir, exist_ok=True)
        return full_path

    async def create_contract_file_path(self, user_id: int) -> Contract:
        existing_contract = await self.get_contract_by_id(user_id=user_id)
        if existing_contract:
            return existing_contract

        file_path = self.generate_file_path("uploads/contract", ".pdf")
        contract_data = ContractCreate(user_id=user_id, file_path=file_path)
        return await super().create(model=Contract, obj_items=contract_data)

    async def get_contract_by_id(self, user_id: int) -> Contract | None:
        return await super().get_by_field(
            model=Contract, field_name="user_id", field_value=user_id
        )

    async def report_generator(self, user_id: int, qr_code_path: str | None = None) -> str:
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

        user = contract.user
        passport = user.passport_data
        study_info = user.study_info
        study_direction = study_info.study_direction if study_info else None

        if not (passport and study_info and study_direction):
            raise HTTPException(status_code=400, detail="Required user info is missing")

        full_name = f"{passport.last_name} {passport.first_name} {passport.third_name or ''}".strip()
        contract_id = ''.join(random.choices('0123456789', k=6))

        return templates.get_template("report.html").render({
            "contract_id": contract_id,
            "date": datetime.datetime.now().strftime("%Y-%m-%d"),
            "fio": full_name,
            "edu_form": study_info.study_form.name if study_info.study_form else "",
            "edu_type": study_info.study_type.name if study_info.study_type else "",
            "edu_year": study_direction.education_years,
            "edu_direction": study_direction.name,
            "contract_price": study_direction.contract_sum,
            "address": passport.address or "",
            "passport_id": passport.passport_series_number or "",
            "jshir": passport.jshshir or "",
            "phone_number": user.phone_number or "",
            "qr_code_path": qr_code_path,
        })

    async def download_pdf(self, user_id: int) -> BytesIO:
        contract = await self.get_contract_by_id(user_id)
        if not contract:
            contract = await self.create_contract_file_path(user_id)

        html_content = await self.add_qr_code_in_report(user_id)

        pdf = BytesIO()
        HTML(string=html_content, base_url=".").write_pdf(pdf)
        pdf.seek(0)

        # Save the file to disk
        os.makedirs(os.path.dirname(contract.file_path), exist_ok=True)
        with open(contract.file_path, "wb") as f:
            f.write(pdf.read())
        pdf.seek(0)

        return pdf

    async def add_qr_code_in_report(self, user_id: int) -> str:
        contract = await self.get_contract_by_id(user_id=user_id)
        if not contract:
            raise HTTPException(status_code=404, detail="Contract not found")

        qr_path = self.generate_file_path("uploads/media/qr_codes", ".png")
        file_url = f"http://example.com/{contract.file_path}"  # Update with actual host if needed
        self.generate_qr_code(data=file_url, save_path=qr_path)

        return await self.report_generator(user_id=user_id, qr_code_path=qr_path)

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



class ContractService(BasicCrud):
    def __init__(self, db: AsyncSession):
        super().__init__(db)

    async def get_contract_by_user_id(self, user_id: int):
        return await super().get_by_field(
            model=Contract,
            field_name="user_id",
            field_value=user_id
        )

    async def get_all_contracts(self, limit: int = 10, offset: int = 0):
        return await super().get_all(
            model=Contract,
            limit=limit,
            offset=offset
        )

    async def update_contract_status(self, user_id: int):
        contract = await self.get_contract_by_user_id(user_id=user_id)
        contract.status = True

        self.db.add(contract)
        await self.db.commit()
        await self.db.refresh(contract)

        return contract
