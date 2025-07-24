from pydantic import BaseModel
from typing import Optional

class DomainRequest(BaseModel):
    domain: str

class DomainResponse(BaseModel):
    domain: str
    registered: bool
    expires: Optional[str] = None
