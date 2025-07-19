from fastapi import APIRouter, Depends
from src.core.db import get_db
from src.service.contract import ContractService
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

contract_router = APIRouter(prefix="/contracts", tags=["Contracts"])

def get_contract_service(db: AsyncSession = Depends(get_db)):
    return ContractService(db)

@contract_router.get("/user/{user_id}")
async def get_user_contract(
    user_id: int,
    service: Annotated[ContractService, Depends(get_contract_service)]
):
    return await service.get_contract_by_user_id(user_id=user_id)

@contract_router.get("/")
async def get_all_contracts(
    service: Annotated[ContractService, Depends(get_contract_service)]
):
    return await service.get_all_contracts()

@contract_router.patch("/user/{user_id}/status")
async def update_contract_status(
    user_id: int,
    service: Annotated[ContractService, Depends(get_contract_service)]
):
    return await service.update_contract_status(user_id=user_id)
