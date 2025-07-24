from pydantic import BaseModel

class ContractBase(BaseModel):
    file_path: str | None = None
    
    
class ContractCreate(ContractBase):
    user_id: int
    status: bool

    