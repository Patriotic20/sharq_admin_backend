from pydantic import BaseModel , ConfigDict
from src.schemas.passport_data import PassportDataResponse
from src.schemas.study_info import StudyInfoResponse


class UserDataResponse(BaseModel):
    passport_data: PassportDataResponse
    study_info_data: StudyInfoResponse
    
    model_config = ConfigDict(from_attributes=True)


class UserDataFilterByPassportData(BaseModel):
    passport_series_number: str   | None = None
    jshshir: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    third_name: str | None = None
    region: str | None = None
    gender: str | None = None
    


class UserDataFilterByStudyInfo(BaseModel):
    study_language: str | None = None
    study_form: str | None = None
    study_direction_name: str | None = None 
    education_type: str | None = None
    study_type: str | None = None
