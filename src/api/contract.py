from fastapi import APIRouter, Depends ,  HTTPException
from src.core.db import get_db
from src.service.contract import ContractService
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from fastapi.responses import StreamingResponse
from sharq_models.models import User  # type: ignore
from src.utils.auth import require_roles
from src.service.contract import ReportService

contract_router = APIRouter(prefix="/contracts", tags=["Contracts"])

def get_contract_service(db: AsyncSession = Depends(get_db)):
    return ContractService(db)

@contract_router.get("/user/{user_id}")
async def get_user_contract(
    user_id: int,
    _: Annotated[User, Depends(require_roles(["admin"]))],
    service: Annotated[ContractService, Depends(get_contract_service)]
):
    return await service.get_contract_by_user_id(user_id=user_id)

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



def get_report_service(db: AsyncSession = Depends(get_db)) -> ReportService:
    return ReportService(db)


@contract_router.post("/create_contract_file_path")
async def create_file_path(
    user_id: int,
    _: Annotated[User, Depends(require_roles(["admin"]))],
    service: Annotated[ReportService, Depends(get_report_service)]
):
    return await service.create_contract_file_path(user_id=user_id)

@contract_router.get(
    "/download",
    response_class=StreamingResponse,
    status_code=200,
    summary="Download user's contract report",
    description="Generates and returns a PDF report for the authenticated user."
)
async def download_report(
    user_id: int,
    _: Annotated[User, Depends(require_roles(["admin"]))],
    service: ReportService = Depends(get_report_service),
):
    try:
        pdf_file = await service.download_pdf(user_id)
        return StreamingResponse(
            pdf_file,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=report_{user_id}.pdf"}
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
