from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import date
from decimal import Decimal

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
    idtarjeta: str
    idcuenta: str
    idtipometodopago: int
    activometodopagocuenta: bool

class DominioCreate(BaseModel):
    iddominio: str
    nombrepagina: str
    preciodominio: Decimal
    ocupado: bool
    identificacion: str  # este campo extra para poder asociar el dominio a la cuenta

class CarritoCreate(BaseModel):
    idestadocarrito: str
    idcuenta: str
    idmetodopagocuenta: str

class CarritoDominioCreate(BaseModel):
    iddominio: str
    idcarrito: int
    idcarritodominio: str

class CarritoUpdate(BaseModel):
    idcarrito: int
    idestadocarrito: str

class CarritoDominioDelete(BaseModel):
    iddominio: str
    idcarrito: int
    idcarritodominio: str

class DominioEnCarrito(BaseModel):
    cuenta: str
    carrito: int
    iddominio: str
    dominio: str
    precio: float

class FacturaCreate(BaseModel):
    idcarrito: int

class CarritoEstadoUpdate(BaseModel):
    idcarrito: int

class LoginRequest(BaseModel):
    identificacion: str
    password: str

class ActualizarOcupadoDominioRequest(BaseModel):
    iddominio: str
    ocupado: bool

class MetodoPagoUsuario(BaseModel):
    identificacion: str
    numerotarjeta: str
    tipotarjeta: int

class ListaMetodoPagoResponse(BaseModel):
    metodos_pago: List[MetodoPagoUsuario]

class AgregarDominioRequest(BaseModel):
    iddominio: str
    idcuenta: str

class TarjetaRequest(BaseModel):
    numero_tarjeta: str
    ccv: str
    fecha_vto: str
    id_cuenta: str