import os
import random
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

class ContractBase:
    BASE_UPLOAD_DIR = "uploads"

    def path_builder(self, base_dir: str, extension: str) -> str:
        return f"{self.BASE_UPLOAD_DIR}/{base_dir}/{extension}"
    
    def url_builder(self, base_dir: str, extension: str) -> str:
        return f"{settings.base_url}/{self.BASE_UPLOAD_DIR}/{base_dir}/{extension}"
    
    def generate_file_path(self, base_dir: str, extension: str) -> str:
        filename = f"{uuid4().hex}{extension}"
        return os.path.join(base_dir, filename)

class ContractService(BasicCrud, ContractBase):
    CONTRACT_CONFIG = {
        "two_side": {
            "directory": "contract_two_side",
            "template": "ikki.html",
            "is_three": False,
        },
        "three_side": {
            "directory": "contract_three_side",
            "template": "uchtomon.html",
            "is_three": True,
        }
    }
    
    def __init__(self, db: AsyncSession):
        super().__init__(db=db)
        self.qr_code_dir_path = self.path_builder("qr_codes", ".png")
        
        
    async def generate_contracts(self, user_id: int, edu_course_level: int):
        for contract_type in self.CONTRACT_CONFIG:
            await self.contract_download_pdf(user_id=user_id, edu_course_level=edu_course_level, contract_type=contract_type)

        
    async def contract_download_pdf(self, user_id: int, edu_course_level: int, contract_type: str = "two_side") -> str:
        contract = await self._get_contract(user_id)
        
        if contract and contract.file_path and contract_type in contract.file_path:
            return urlparse(contract.file_path).path.lstrip("/")
        
        contract = await self._create_contract(self.CONTRACT_CONFIG[contract_type]["directory"], ".pdf", user_id)
        html_content = await self._add_qr_code_and_generate_html(user_id, edu_course_level, contract_type)
        file_path = urlparse(contract.file_path).path.lstrip("/")
        
        self._save_contract_pdf(html_content, file_path)
        return file_path


    async def _create_contract(self, base_dir: str, extension: str, user_id: int) -> Contract:
        file_path = self.generate_file_path(base_dir, extension)
        contract_data = ContractCreate(user_id=user_id, file_path=file_path, status=True)
        return await super().create(model=Contract, obj_items=contract_data)

    async def _get_contract(self, user_id: int) -> Contract:
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
       

    def _generate_qr_code(self, data: str, save_path: str) -> None:
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

    def _get_full_name(self, passport) -> str:
        return " ".join(filter(None, [passport.last_name, passport.first_name, passport.third_name]))

    def _generate_contract_id(self) -> str:
        return str(random.randint(0, 999999)).zfill(6)

    async def _generate_contract_html(self, user_id: int, template_name: str, edu_course_level: int, qr_code_path: str = None) -> str:
        contract = await self.get_contract(user_id, load_related=True)
        user = contract.user
        passport = user.passport_data
        study_info = user.study_info
        direction = study_info.study_direction if study_info else None
        if not (passport and study_info and direction):
            raise HTTPException(status_code=400, detail="Required user info is missing")
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
        return templates.get_template(template_name).render(context)

    async def _add_qr_code_and_generate_html(self, user_id: int, edu_course_level: int, contract_type: str) -> str:
        contract = await self.get_contract(user_id)
        qr_path = self.generate_file_path(self.qr_code_dir_path, ".png")
        self._generate_qr_code(data=contract.file_path, save_path=qr_path)
        template_name = self.CONTRACT_CONFIG[contract_type]["template"]
        return await self._generate_contract_html(user_id, template_name, edu_course_level, qr_code_path=qr_path)

    def _save_contract_pdf(self, html_content: str, file_path: str) -> None:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "wb") as f:
            HTML(string=html_content, base_url=".").write_pdf(f)


        
        
        
