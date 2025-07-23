from fastapi import APIRouter, Depends  , HTTPException
from fastapi.responses import  FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.db import get_db
from src.service.report import ReportService
from typing import Annotated
from sharq_models.models import User # type: ignore
from src.utils.auth import require_roles 
import os

report_router = APIRouter(prefix="/contract", tags=["Contract Reports"])


def get_report_service(db: AsyncSession = Depends(get_db)):
    return ReportService(db)


@report_router.get("/download/ikki/{user_id}")
async def download_ikki_pdf(
    user_id: int,
    service: Annotated[ReportService , Depends(get_report_service)],
    _: Annotated[User, Depends(require_roles(["admin"]))],
    is_three: bool = False,
):
    file_path = await service.download_pdf(user_id=user_id, is_three=is_three)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        path=file_path,
        filename=os.path.basename(file_path),
        media_type="application/pdf"
    )





