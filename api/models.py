from pydantic import BaseModel
from typing import List, Optional

class DomainRequest(BaseModel):
    domain: str  # sin extensión

class DomainStatus(BaseModel):
    domain: str
    registered: bool
    expires: Optional[str] = None  # puede ser None si no está registrado

class AlternativesResponse(BaseModel):
    domain: str
    alternativas: List[DomainStatus]

class DominioPago(BaseModel):
    iddominio: str
    precio: float

class PagoRequest(BaseModel):
    idcuenta: str
    idmetodopago: int
    idcuentametodopago: str
    dominios: list[DominioPago]