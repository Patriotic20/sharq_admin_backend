from fastapi import APIRouter
from .study_direction import study_direction_router
from .education_type import education_type_router
from .study_type import study_type_router
from .study_language import study_language_router
from .passport_data import passport_data_router
from .study_form import study_form_router
from .study_info import study_info_router
from .auth import auth_router
from .role import role_router
from .contract import contract_router
from .user_data import user_data_router
from .report import report_router


api_router = APIRouter(prefix="/api")

api_router.include_router(auth_router)
api_router.include_router(study_language_router)
api_router.include_router(education_type_router)
api_router.include_router(study_type_router)
api_router.include_router(study_form_router)
api_router.include_router(study_direction_router)
api_router.include_router(study_info_router)
api_router.include_router(passport_data_router)
api_router.include_router(role_router)
api_router.include_router(contract_router)
api_router.include_router(user_data_router)
api_router.include_router(report_router)

