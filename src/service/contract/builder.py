from datetime import datetime
import logging
from urllib.parse import urlparse
from typing import Optional

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.contract import ContractCreate
from sharq_models.models import Contract, User, StudyInfo, AMOCrmLead  # type: ignore
from src.service.contract.base import ContractBase
from src.utils.utils import number_to_uzbek
from src.service.contract.amo import move_lead_to_get_contract_pipeline
from src.core.config import settings

class ContractService(ContractBase):
    def __init__(self, db: AsyncSession):
        super().__init__(db=db)
        self.logger = logging.getLogger(__name__)
        
    async def generate_contracts(self, user_id: int, edu_course_level: int):
        urls = []
        lead = await self._get_lead(user_id)
        if lead:
            move_lead_to_get_contract_pipeline(lead.lead_id, settings.amo_crm_config)
        else:
            self.logger.error(f"Lead not found for user {user_id}")
        
        for contract_type in self.CONTRACT_CONFIG:
            url = await self.get_or_create_contract(user_id=user_id, edu_course_level=edu_course_level, contract_type=contract_type)
            urls.append(url)
        return urls
    
    async def get_contracts(
        self, 
        # limit: int = 10, 
        # offset: int = 0
        ) -> list[Contract]:

        stmt = (
            select(Contract)
            .options(
                joinedload(Contract.user).joinedload(User.passport_data),
                joinedload(Contract.user).joinedload(User.study_info).joinedload(StudyInfo.study_form),
                joinedload(Contract.user).joinedload(User.study_info).joinedload(StudyInfo.study_type),
                joinedload(Contract.user).joinedload(User.study_info).joinedload(StudyInfo.study_direction),
            )
            .order_by(Contract.created_at.desc())
            # .limit(limit)
            # .offset(offset)
        )
        result = await self.db.execute(stmt)
        contracts = result.scalars().all()
        return contracts
    
    async def _get_lead(self, user_id: int) -> AMOCrmLead:
        stmt = (
            select(AMOCrmLead)
            .where(AMOCrmLead.user_id == user_id)
        )
        result = await self.db.execute(stmt)
        lead = result.scalars().first()
        return lead

    async def get_or_create_contract(self, user_id: int, contract_type: str = "two_side", edu_course_level: Optional[int] = None) -> str:
        contract, is_created = await self._create_contract_or_get_existing(user_id, contract_type)
        
        if contract and contract.contract_type == contract_type and not is_created:
            if not contract.file_url:
                raise HTTPException(status_code=404, detail="File not found")
            
            return urlparse(contract.file_url).path.lstrip("/")
        
        context = await self._prepare_contract_context(contract, edu_course_level)
        html_content = self._render_contract_html(self.CONTRACT_CONFIG[contract_type]["template"], context)
        file_url = urlparse(contract.file_url).path.lstrip("/")

        self._save_contract_pdf(html_content, file_url)
        return file_url

    async def _create_contract_or_get_existing(self, user_id: int, contract_type: str) -> Contract:
        existing_contract = await self._get_contract(user_id, contract_type)
        
        if not existing_contract:
            file_path = self.path_builder(contract_type, ".pdf")
            contract =  await super().create(
                model=Contract, 
                obj_items=ContractCreate(
                    user_id=user_id, 
                    file_path=file_path, 
                    file_url=self.url_builder(file_path),
                    status=True,
                    contract_id=self._generate_contract_id(),
                    contract_type=contract_type
                )
            )    

            if not contract:
                raise HTTPException(status_code=404, detail="Contract not found for this user")
            
            await self._update_in_study_info(user_id=user_id)
            
            full_contract = await self._get_contract(user_id, contract_type)            
            return full_contract, True
        else:
            return existing_contract, False
        
    async def _get_contract(self, user_id: int, contract_type: str) -> Contract:
        stmt = (
            select(Contract)
            .options(
                joinedload(Contract.user),
                joinedload(Contract.user).joinedload(User.passport_data),
                joinedload(Contract.user).joinedload(User.study_info).joinedload(StudyInfo.study_form),
                joinedload(Contract.user).joinedload(User.study_info).joinedload(StudyInfo.study_type),
                joinedload(Contract.user).joinedload(User.study_info).joinedload(StudyInfo.study_direction),
            )
            .where(Contract.user_id == user_id, Contract.contract_type == contract_type)
        )
        result = await self.db.execute(stmt)
        contract = result.scalars().first()
        return contract
    
    async def _prepare_contract_context(self, contract: Contract, edu_course_level: int) -> dict:
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
            "contract_price": f"{direction.contract_sum} ({number_to_uzbek(int(direction.contract_sum))})",
            "address": passport.address or "",
            "passport_id": passport.passport_series_number or "",
            "jshir": passport.jshshir or "",
            "phone_number": user.phone_number or "",
            "contract_file_path": contract.file_url,
            "contract_date": str(datetime.now().strftime("%d.%m.%Y")),
        }
        return context


        
