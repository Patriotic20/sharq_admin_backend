from fastapi import APIRouter, Depends , Query
from src.service.study_info import StudyInfoCrud
from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas.study_info import StudyInfoResponse, StudyInfoCreate , StudyInfoListResponse
from src.schemas.user_data import UserDataFilterByPassportData , UserDataFilterByStudyInfo
from dto.study_info_filter import QueryUserDataFilterByPassport , QueryUserDataFilterByStudy
from src.core.db import get_db
from fastapi.responses import StreamingResponse
from sharq_models import User #type: ignore
from src.utils.auth import require_roles
from typing import Annotated

study_info_router = APIRouter(prefix="/study_info", tags=["Study Info"])


def get_service_crud(db: AsyncSession = Depends(get_db)):
    return StudyInfoCrud(db)


@study_info_router.get("/get_by_id/{study_info_id}")
async def get_by_study_info_id(
    study_info_id: int,
    service: Annotated[StudyInfoCrud, Depends(get_service_crud)],
    _: Annotated[User, Depends(require_roles(["admin"]))],
) -> StudyInfoResponse:
    return await service.get_study_info_by_id(study_info_id=study_info_id)


@study_info_router.get("/applications" , response_model=StudyInfoListResponse)
async def get_study_info_form_filter(
    service: Annotated[StudyInfoCrud, Depends(get_service_crud)],
    _: Annotated[User, Depends(require_roles(["admin"]))],
    query_passport: QueryUserDataFilterByPassport = Depends(),
    query_study: QueryUserDataFilterByStudy = Depends(),
    search: str | None = Query(None),
    limit: int = Query(100),
    offset: int = Query(0),
):
    passport_filter = UserDataFilterByPassportData(**query_passport.__dict__)
    study_info_filter = UserDataFilterByStudyInfo(**query_study.__dict__)

    result = await service.get_all_study_info(
        passport_filter=passport_filter,
        study_info_filter=study_info_filter,
        limit=limit,
        offset=offset,
        search=search
    )
    return result
    
    
@study_info_router.get("/study-info/excel")
async def download_study_info_excel(
    service: Annotated[StudyInfoCrud, Depends(get_service_crud)],
    _: Annotated[User, Depends(require_roles(["admin"]))],
):
    stream = await service.export_to_excel()
    return StreamingResponse(
        stream,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=Student_ariza.xlsx"}
    )
    
    
@study_info_router.post("/create")
async def create_study_info(
    study_info: StudyInfoCreate,
    service: Annotated[StudyInfoCrud, Depends(get_service_crud)],
    _: Annotated[User, Depends(require_roles(["admin"]))],
):
    return await service.create_study_info(study_info_data=study_info)



@study_info_router.delete("/delete")
async def delete_study_info(
    service: Annotated[StudyInfoCrud, Depends(get_service_crud)],
    _: Annotated[User, Depends(require_roles(["admin"]))],
    user_id: int | None = None,
    study_info_id: int | None = None,
    
):
    return await service.delete_study_info(user_id=user_id , study_info_id=study_info_id)
    
