from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import date

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

class RolUsuarioResponse(BaseModel):
    nombrecuenta: str
    nombretipo: str

class CuentaCreate(BaseModel):
    identificacion: str
    nombrecuenta: str
    correo: str
    telefono: int
    direccion: str
    idtipocuenta: int
    idpais: int
    idplan: str
    password: str


class TarjetaCreate(BaseModel):
    idtipotarjeta: int
    numerotarjeta: int
    ccv: int
    fechavto: date

class MetodoPagoCuentaCreate(BaseModel):
    idmetodopagocuenta: str
    idtarjeta: str
    idcuenta: str
    idtipometodopago: int
    activometodopagocuenta: bool
