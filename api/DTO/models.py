from pydantic import BaseModel, EmailStr,field_validator
from typing import List, Optional, Literal
from datetime import date
from decimal import Decimal
from pydantic import StringConstraints
from typing import Annotated

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

class ActualizarOcupadoDominioRequestList(BaseModel):
    dominios: List[ActualizarOcupadoDominioRequest]

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

class TarjetaValidarResponse(BaseModel):
    valid: bool 
    mensaje: str

class TransferenciaDominioRequest(BaseModel):
    iddominio: str 
    idcuenta_origen: str  
    correo_destino: str 

class DominioAdquiridoRequest(BaseModel):
    idcuenta: str

class ObtenerFacturasRequest(BaseModel):
    idcuenta: str 

class InfoPlanCreate(BaseModel):
    idinfoplan: str
    nombreplan: str
    precio: Decimal
    numsitiosweb: int
    numbd: int
    almacenamiento: str
    correos: int
    numcertificadosssl: int
    duracion: int

class PeriodicidadPrecioInput(BaseModel):
    idperiodicidadpago: str
    precio: float


class PaqueteHostingInput(BaseModel):
    idpaquetehosting: str
    nombrepaquetehosting: str
    cantidadsitios: int
    bd: int
    gbenssd: int
    correos: int
    certificadossslhttps: int
    precios: List[PeriodicidadPrecioInput]

class CrearPlanRequest(BaseModel):
    cantidadsitios: int
    nombrepaquetehosting: str
    bd: int
    gbenssd: int
    correos: int
    certificadosslhttps: int
    nombreperiodicidad: Literal["MENSUAL", "SEMESTRAL", "ANUAL"]  # 1: mensual, 6: semestral, 12: anual
    preciopaquete: int

class CuentaNombreCorreo(BaseModel):
    nombrecuenta: str
    correo: str

class CorreoRequest(BaseModel):
    correo: EmailStr

class CuentaResponse(BaseModel):
    IDCUENTA: str
    IDTIPOCUENTA: int
    IDPAIS: int
    IDPLAN: Optional[int]
    IDENTIFICACION: str
    NOMBRECUENTA: str
    CORREO: EmailStr
    TELEFONO: int
    FECHAREGISTRO: date
    DIRECCION: Optional[str]

class ComisionUpdateRequest(BaseModel):
    idplan: str
    comision: Decimal
    limitedominios: int

class MiPlanResponse(BaseModel):
    idplan: int
    nombreplan: str
    comision: int
    limitedominios: int

class CambiarPlanRequest(BaseModel):
    idcuenta: str
    idplan: str

class PlanResponse(BaseModel):
    idplan: int
    nombreplan: str
    comision: float
    limitedominios: int

class CrearPaqueteRequest(BaseModel):
    cantidadsitios: int
    nombrepaquetehosting: str
    bd: int
    gbenssd: int
    correos: int
    certificadosslhttps: int
    preciopaquete: float
    periodicidad: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=3)]

    @field_validator("periodicidad")
    def validar_rango_periodicidad(cls, v):
        if not v.isdigit():
            raise ValueError("La periodicidad debe ser un número entre 1 y 365")
        valor = int(v)
        if not 1 <= valor <= 365:
            raise ValueError("La periodicidad debe estar entre 1 y 365 días")
        return v

class InfoPaqueteResponse(BaseModel):
    cantidadsitios: int
    nombrepaquetehosting: str
    bd: int
    gbenssd: int
    correos: int
    certificadosslhttps: int

class PaqueteResponse(BaseModel):
    idpaquetehosting: int
    preciopaquete: float
    periodicidad: str
    info: InfoPaqueteResponse

class MiPaqueteResponse(BaseModel):
    idfacturapaquete: int
    fchpago: date
    fchvencimiento: date
    estado: int
    valorfp: float
    preciopaquete: float
    periodicidad: str
    info: InfoPaqueteResponse

class ComprarPaqueteRequest(BaseModel):
    idcuenta: str
    idpaquetehosting: int
    estado: int