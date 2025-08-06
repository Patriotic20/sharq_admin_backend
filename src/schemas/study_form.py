from pydantic import BaseModel, ConfigDict
from typing import Optional


class StudyFormBase(BaseModel):
    name: str


class StudyFormResponse(StudyFormBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class StudyFormFilter(BaseModel):
    name: Optional[str] = None


class StudyFormUpdate(BaseModel):
    name: Optional[str] = None
