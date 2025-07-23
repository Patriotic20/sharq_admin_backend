from fastapi import APIRouter, Depends
from src.core.db import get_db
from src.service.contract import ContractService
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from sharq_models.models import User  # type: ignore
from src.utils.auth import require_roles

contract_router = APIRouter(prefix="/contracts", tags=["Contracts"])

def get_contract_service(db: AsyncSession = Depends(get_db)):
    return ContractService(db)

@contract_router.post("/{user_id}")
async def create_contractmodel(
    user_id: int,
    edu_course_level: int,
    _: Annotated[User, Depends(require_roles(["admin"]))],
    service: Annotated[ContractService, Depends(get_contract_service)]
    
):
    return await service.create_contract_file_path(user_id=user_id , edu_course_level=edu_course_level)

@contract_router.get("/user/{user_id}")
async def get_user_contract(
    user_id: int,
    _: Annotated[User, Depends(require_roles(["admin"]))],
    service: Annotated[ContractService, Depends(get_contract_service)]
):
    return await service.get_contract_by_id(user_id=user_id)

@contract_router.get("/")
async def get_all_contracts(
    _: Annotated[User, Depends(require_roles(["admin"]))],
    service: Annotated[ContractService, Depends(get_contract_service)]
):
    return await service.get_all_contracts()

@contract_router.patch("/user/{user_id}/status")
async def update_contract_status(
    user_id: int,
    _: Annotated[User, Depends(require_roles(["admin"]))],
    service: Annotated[ContractService, Depends(get_contract_service)]
):
    return await service.update_contract_status(user_id=user_id)



