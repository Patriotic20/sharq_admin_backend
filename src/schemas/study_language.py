from pydantic import BaseModel, ConfigDict
from typing import Optional


class StudyLanguageBase(BaseModel):
    name: str


class StudyLanguageResponse(StudyLanguageBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class StudyLanguageFilter(BaseModel):
    name: Optional[str] = None


class StudyLanguageUpdate(BaseModel):
    name: Optional[str] = None
