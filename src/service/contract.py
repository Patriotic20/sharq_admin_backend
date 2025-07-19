from sqlalchemy.ext.asyncio import AsyncSession
from src.service import BasicCrud
from sharq_models.models import Contract  # type: ignore

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
