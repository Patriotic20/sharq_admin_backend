from pydantic import BaseModel, ConfigDict
from datetime import date
from .study_language import StudyLanguageResponse
from .study_form import StudyFormResponse
from .study_direction import StudyDirectionResponse
from .education_type import EducationTypeResponse
from .study_type import StudyTypeResponse
from .passport_data import PassportDataResponse

class StudyInfoBase(BaseModel):
    study_language_id: int
    study_form_id: int
    study_direction_id: int
    study_type_id: int
    education_type_id: int
    graduate_year: str
    certificate_path: str | None = None
    dtm_sheet: str | None = None
    
class StudyInfoCreate(StudyInfoBase):
    user_id: int
    promo_code: str | None = None


class StudyInfoCreateRequest(StudyInfoBase):
    pass


class StudyInfoResponse(BaseModel):
    id: int
    user_id: int

    study_language: StudyLanguageResponse
    study_form: StudyFormResponse
    study_direction: StudyDirectionResponse
    education_type: EducationTypeResponse
    study_type: StudyTypeResponse
    
    graduate_year: str | None = None
    certificate_path: str  | None = None
    dtm_sheet: str  | None = None
    is_approved: bool | None = False
    contract_paths: list[str] = [] 
    passport_data: PassportDataResponse | None = None
    phone_number: str | None
    create_at: date
    
    model_config = ConfigDict(from_attributes=True)


class StudyInfoListResponse(BaseModel):
    data: list[StudyInfoResponse]
    total: int

