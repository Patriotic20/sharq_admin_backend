from pydantic import BaseModel

class ContractBase(BaseModel):
    file_path: str | None = None
    file_url: str | None = None
    
    
class ContractCreate(ContractBase):
    user_id: int
    status: bool
    contract_type: str
    

    