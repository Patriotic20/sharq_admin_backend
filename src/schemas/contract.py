from pydantic import BaseModel

class ContractBase(BaseModel):
    file_path: str
    
    
class ContractCreate(ContractBase):
    user_id: int
    
    