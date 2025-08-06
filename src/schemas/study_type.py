from pydantic import BaseModel, ConfigDict
from typing import Optional


class StudyTypeBase(BaseModel):
    name: str


class StudyTypeResponse(StudyTypeBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class StudyTypeFilter(BaseModel):
    name: Optional[str] = None


class StudyTypeUpdate(BaseModel):
    name: Optional[str] = None
