from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
import os

from src.core.db import get_db
from src.service.report import ReportService
from sharq_models.models import User  # type: ignore
from src.utils.auth import require_roles

report_router = APIRouter(prefix="/contract", tags=["Contract Reports"])


def get_report_service(db: AsyncSession = Depends(get_db)):
    return ReportService(db)


@report_router.post("")
async def generate_both_report(
    user_id: int,
    edu_course_level: int,
    service: Annotated[ReportService, Depends(get_report_service)],
    _: Annotated[User, Depends(require_roles(["admin"]))],
):
    await service.generate_both_report(user_id=user_id, edu_course_level=edu_course_level)
    return {"message": "Generated successfully"}


@report_router.get("/download/ikki/{user_id}")
async def download_ikki_pdf(
    user_id: int,
    service: Annotated[ReportService, Depends(get_report_service)],
    _: Annotated[User, Depends(require_roles(["admin"]))],
):
    file_path = await service.get_two_side_report(user_id=user_id)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        path=file_path,
        filename=os.path.basename(file_path),
        media_type="application/pdf"
    )


@report_router.get("/download/uch/{user_id}")  
async def download_uch_pdf(
    user_id: int,
    service: Annotated[ReportService, Depends(get_report_service)],
    _: Annotated[User, Depends(require_roles(["admin"]))],
):
    file_path = await service.get_three_side_report(user_id=user_id)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        path=file_path,
        filename=os.path.basename(file_path),
        media_type="application/pdf"
    )







