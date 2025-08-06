from fastapi import APIRouter, Depends, HTTPException 
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
import os

from src.core.db import get_db
from src.service.contract import ContractService
from sharq_models.models import User  # type: ignore
from src.utils.auth import require_roles

contract_router = APIRouter(prefix="/contract", tags=["Contracts"])


def get_contract_service(db: AsyncSession = Depends(get_db)):
    return ContractService(db)

class GenerateContractsRequest(BaseModel):
    user_id: int
    edu_course_level: int


@contract_router.post("")
async def generate_contracts(
    request: GenerateContractsRequest,
    service: Annotated[ContractService, Depends(get_contract_service)],
    _: Annotated[User, Depends(require_roles(["admin"]))],
):
    urls = await service.generate_contracts(user_id=request.user_id, edu_course_level=request.edu_course_level)
    return {"message": "Generated successfully", "urls": urls}


@contract_router.get("/download/ikki/{user_id}")
async def download_ikki_pdf(
    user_id: int,
    service: Annotated[ContractService, Depends(get_contract_service)],
    _: Annotated[User, Depends(require_roles(["admin"]))],
):
    file_path = await service.get_or_create_contract(user_id=user_id, contract_type="two_side")

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        path=file_path,
        filename=os.path.basename(file_path),
        media_type="application/pdf"
    )


@contract_router.get("/download/uch/{user_id}")  
async def download_uch_pdf(
    user_id: int,
    service: Annotated[ContractService, Depends(get_contract_service)],
    _: Annotated[User, Depends(require_roles(["admin"]))],
):
    file_path = await service.get_or_create_contract(user_id=user_id, contract_type="three_side")

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        path=file_path,
        filename=os.path.basename(file_path),
        media_type="application/pdf"
    )


@contract_router.get("/get_all")
async def get_all_contract_data(
    service: Annotated[ContractService, Depends(get_contract_service)],
    _: Annotated[User, Depends(require_roles(["admin"]))],
):
    return await service.get_contracts()





