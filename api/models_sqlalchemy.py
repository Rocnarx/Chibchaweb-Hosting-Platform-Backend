from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Float, Boolean, Integer, ForeignKey, Numeric, Date
from sqlalchemy.orm import relationship

Base = declarative_base()

class TipoCuenta(Base):
    __tablename__ = "TIPOCUENTA"

    IDTIPOCUENTA = Column("IDTIPOCUENTA", Numeric(2), primary_key=True)
    NOMBRETIPO = Column("NOMBRETIPO", String(30), nullable=False)

    CUENTAS = relationship("Cuenta", back_populates="TIPOCUENTA_REL")


from sqlalchemy.orm import relationship

class Cuenta(Base):
    __tablename__ = "CUENTA"

    IDCUENTA = Column("IDCUENTA", String(15), primary_key=True)
    IDTIPOCUENTA = Column("IDTIPOCUENTA", Numeric(2), ForeignKey("TIPOCUENTA.IDTIPOCUENTA"), nullable=False)
    IDPAIS = Column("IDPAIS", Numeric(3), ForeignKey("PAIS.IDPAIS"), nullable=False)
    IDPLAN = Column("IDPLAN", String(15), ForeignKey("PLAN.IDPLAN"), nullable=True)

    PASSWORD = Column("PASSWORD", String(50), nullable=False)
    IDENTIFICACION = Column("IDENTIFICACION", String(15), nullable=False)
    NOMBRECUENTA = Column("NOMBRECUENTA", String(150), nullable=False)
    CORREO = Column("CORREO", String(50), nullable=False)
    TELEFONO = Column("TELEFONO", Integer, nullable=False)
    FECHAREGISTRO = Column("FECHAREGISTRO", Date, nullable=False)
    DIRECCION = Column("DIRECCION", String(30))

    # Relaciones
    TIPOCUENTA_REL = relationship("TipoCuenta", back_populates="CUENTAS")
    PAIS_REL = relationship("Pais", back_populates="CUENTAS")
    PLAN_REL = relationship("Plan", back_populates="CUENTAS")
    METODOSPAGO = relationship("MetodoPagoCuenta", back_populates="CUENTA_REL")





class Plan(Base):
    __tablename__ = "PLAN"

    IDPLAN = Column(String(15), primary_key=True)
    NOMBREPLAN = Column(String(15), nullable=False)
    COMISION = Column(Numeric(2), nullable=False)

    CUENTAS = relationship("Cuenta", back_populates="PLAN_REL")



class Pais(Base):
    __tablename__ = "PAIS"

    IDPAIS = Column(Numeric(3), primary_key=True)
    NOMBREPAIS = Column(String(15), nullable=False)

    CUENTAS = relationship("Cuenta", back_populates="PAIS_REL")



class Tarjeta(Base):
    __tablename__ = "TARJETA"

    IDTARJETA = Column("IDTARJETA", Integer, primary_key=True, autoincrement=True)
    IDTIPOTARJETA = Column("IDTIPOTARJETA", Numeric(2), nullable=False)
    NUMEROTARJETA = Column("NUMEROTARJETA", Numeric(15), nullable=False)
    CCV = Column("CCV", Numeric(3), nullable=False)
    FECHAVTO = Column("FECHAVTO", Date, nullable=False)


class MetodoPagoCuenta(Base):
    __tablename__ = "METODOPAGOCUENTA"

    IDMETODOPAGOCUENTA = Column("IDMETODOPAGOCUENTA", String(3), primary_key=True)
    IDTARJETA = Column("IDTARJETA", String(15), ForeignKey("TARJETA.IDTARJETA"))
    IDCUENTA = Column("IDCUENTA", String(15), ForeignKey("CUENTA.IDCUENTA"))
    IDTIPOMETODOPAGO = Column("IDTIPOMETODOPAGO", Numeric(2), ForeignKey("TIPOMETODOPAGO.IDTIPOMETODOPAGO"))
    ACTIVOMETODOPAGOCUENTA = Column("ACTIVOMETODOPAGOCUENTA", Boolean, nullable=False)

    CUENTA_REL = relationship("Cuenta", back_populates="METODOSPAGO")
    TARJETA_REL = relationship("Tarjeta")  # Ya debe estar si no, agrégala también



class TipoMetodoPago(Base):
    __tablename__ = "TIPOMETODOPAGO"

    IDTIPOMETODOPAGO = Column("IDTIPOMETODOPAGO", Numeric(2), primary_key=True)
    NOMBRETIPOMETODOPAGO = Column("NOMBRETIPOMETODOPAGO", String(15), nullable=False)


class Dominio(Base):
    __tablename__ = "DOMINIO"

    IDDOMINIO = Column("IDDOMINIO", String(150), primary_key=True)
    NOMBREPAGINA = Column("NOMBREPAGINA", String(150), nullable=False)
    PRECIODOMINIO = Column("PRECIODOMINIO", Numeric(10, 2), nullable=False)
    OCUPADO = Column("OCUPADO", Boolean, nullable=False)


class EstadoCarrito(Base):
    __tablename__ = "ESTADOCARRITO"

    IDESTADOCARRITO = Column("IDESTADOCARRITO", String(3), primary_key=True)
    NOMESTADOCARRITO = Column("NOMESTADOCARRITO", String(30), nullable=False)


class Carrito(Base):
    __tablename__ = "CARRITO"

    IDCARRITO = Column("IDCARRITO", Integer, primary_key=True, autoincrement=True)
    IDESTADOCARRITO = Column("IDESTADOCARRITO", String(3), ForeignKey("ESTADOCARRITO.IDESTADOCARRITO"), nullable=False)
    IDCUENTA = Column("IDCUENTA", String(15), ForeignKey("CUENTA.IDCUENTA"), nullable=False)
    IDMETODOPAGOCUENTA = Column("IDMETODOPAGOCUENTA", String(3), ForeignKey("METODOPAGOCUENTA.IDMETODOPAGOCUENTA"), nullable=False)


class CarritoDominio(Base):
    __tablename__ = "CARRITODOMINIO"

    IDDOMINIO = Column("IDDOMINIO", String(150), ForeignKey("DOMINIO.IDDOMINIO"), primary_key=True)
    IDCARRITO = Column("IDCARRITO", Integer, ForeignKey("CARRITO.IDCARRITO"), primary_key=True)
    IDCARRITODOMINIO = Column("IDCARRITODOMINIO", String(10), primary_key=True)

class Factura(Base):
    __tablename__ = "FACTURA"

    IDFACTURA = Column("IDFACTURA", Integer, primary_key=True, autoincrement=True)
    IDCARRITO = Column("IDCARRITO", Integer, ForeignKey("CARRITO.IDCARRITO"), nullable=False)
    PAGOFACTURA = Column("PAGOFACTURA", Date, nullable=False)
    VIGFACTURA = Column("VIGFACTURA", Date, nullable=False)