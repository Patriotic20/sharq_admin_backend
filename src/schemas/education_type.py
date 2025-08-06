from pydantic import BaseModel, ConfigDict
from typing import Optional


class EducationTypeBase(BaseModel):
    name: str


class EducationTypeResponse(EducationTypeBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class EducationTypeFilter(BaseModel):
    name: Optional[str] = None


class EducationTypeUpdate(BaseModel):
    name: Optional[str] = None
