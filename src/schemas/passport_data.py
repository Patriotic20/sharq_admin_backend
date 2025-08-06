from pydantic import BaseModel, ConfigDict, Field
from datetime import date



class PassportDataBase(BaseModel):
    passport_series_number: str
    jshshir: str


class PassportDataCreateRequest(PassportDataBase):
    pass


class PersonalInfo(BaseModel):
    jshshir: str = Field(alias="pinfl")
    passport_series_number: str = Field(alias="serialAndNumber")
    gender: str = Field(alias="gender")
    citizenship: str = Field(alias="citizenship")
    nationality: str = Field(alias="nationality")
    date_of_birth: date = Field(alias="birthDate")
    first_name: str = Field(alias="firstName")
    last_name: str = Field(alias="lastName")
    third_name: str = Field(alias="fatherName")
    issue_date: date = Field(alias="givenDate")
    passport_expire_date: date = Field(alias="passportExpireDate")
    country: str = Field(alias="country")
    region: str = Field(alias="region")
    district: str = Field(alias="district")
    address: str = Field(alias="address")
    image_path: str


class PassportDataCreate(PersonalInfo):
    user_id: int


class PassportDataUpdate(BaseModel):
    passport_series_number: str | None = None
    jshshir: str | None = None
    gender: str | None = None
    citizenship: str | None = None
    nationality: str | None = None
    date_of_birth: date | None = None
    first_name: str | None = None
    last_name: str | None = None
    third_name: str | None = None
    issue_date: date | None = None
    passport_expire_date: date | None = None
    country: str | None = None
    region: str | None = None
    district: str | None = None
    address: str | None = None
    image_path: str | None = None

    model_config = ConfigDict(from_attributes=True)

class PassportDataResponse(BaseModel):
    id: int
    user_id: int
    passport_series_number: str
    jshshir: str
    gender: str
    citizenship: str
    nationality: str
    date_of_birth: date
    first_name: str
    last_name: str
    third_name: str
    issue_date: date
    passport_expire_date: date
    country: str
    region: str
    district: str
    address: str
    image_path: str

    model_config = ConfigDict(from_attributes=True)
