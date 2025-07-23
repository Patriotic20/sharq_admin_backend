from sqlalchemy.ext.asyncio import AsyncSession
from sharq_models.models import Contract  # type: ignore
from src.service import BasicCrud
from src.schemas.contract import ContractCreate


class ContractService(BasicCrud):
    def __init__(self, db: AsyncSession):
        super().__init__(db)
        
        
    async def create_contract_file_path(self, user_id: int , edu_course_level: int):
        existing_contract = await self.get_contract_by_id(user_id=user_id)
        if existing_contract:
            return existing_contract
        contract_data = ContractCreate(
            user_id=user_id,
            file_path=None,
            status=True,
            edu_course_level=edu_course_level
            )
        return await super().create(model=Contract, obj_items=contract_data)

        
    async def get_contract_by_id(self, user_id: int) -> Contract | None:
        return await super().get_by_field(
            model=Contract, field_name="user_id", field_value=user_id
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

        await self.db.commit()
        await self.db.refresh(contract)

        return contract
