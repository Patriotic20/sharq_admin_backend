from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.db import get_db
from src.service.report import ReportService
from typing import Annotated
from sharq_models.models import User # type: ignore
from src.utils.auth import require_roles 

report_router = APIRouter(prefix="/contract", tags=["Contract Reports"])


def get_report_service(db: AsyncSession = Depends(get_db)):
    return ReportService(db)


@report_router.get("/download/ikki/{user_id}", summary="Generate 'ikki tomonlama shartnoma' contract PDF")
async def download_ikki_pdf(
    user_id: int,
    _ : Annotated[User, Depends(require_roles(["admin"]))],
    service: Annotated[ReportService , Depends(get_report_service)],
    ):
    pdf_data = await service.download_pdf(user_id)
    return StreamingResponse(
        pdf_data,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=ikki_{user_id}.pdf"}
    )


@report_router.get("/download/uchtomon/{user_id}", summary="Generate 'uchtomonlama shartnoma' contract PDF")
async def download_uchtomon_pdf(
    user_id: int,
    _ : Annotated[User, Depends(require_roles(["admin"]))],
    service: Annotated[ReportService , Depends(get_report_service)],
    ):
    pdf_data = await service.download_3_pdf(user_id)
    return StreamingResponse(
        pdf_data,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=uchtomon_{user_id}.pdf"}
    )




