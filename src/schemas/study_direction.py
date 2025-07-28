from pydantic import BaseModel, ConfigDict



class StudyDirectionBase(BaseModel):
    study_form_id: int | None = None
    name: str 
    exam_title: str 
    
    education_years: int
    contract_sum: float 
    study_code: str 
    



class StudyDirectionResponse(StudyDirectionBase):
    id: int

        
    model_config = ConfigDict(from_attributes=True)


class StudyDirectionUpdate(BaseModel):
    study_form_id: int | None = None
    name: str  | None = None
    exam_title: str  | None = None
    
    education_years: int | None = None
    contract_sum: float  | None = None
    study_code: str  | None = None
    







