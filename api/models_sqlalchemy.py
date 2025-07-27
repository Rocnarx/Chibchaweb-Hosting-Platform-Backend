from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Float, Boolean, Integer, ForeignKey, Numeric, Date
from sqlalchemy.orm import relationship
from . import models


Base = declarative_base()

class TipoCuenta(Base):
    __tablename__ = "TIPOCUENTA"

    idtipocuenta = Column("IDTIPOCUENTA", Numeric(2), primary_key=True)
    nombretipo = Column("NOMBRETIPO", String(30), nullable=False)

    cuentas = relationship("Cuenta", back_populates="tipocuenta")


class Cuenta(Base):
    __tablename__ = "CUENTA"

    idcuenta = Column("IDCUENTA", String(15), primary_key=True)
    idtipocuenta = Column("IDTIPOCUENTA", Numeric(2), ForeignKey("TIPOCUENTA.IDTIPOCUENTA"), nullable=False)
    idpais = Column("IDPAIS", Numeric(3), ForeignKey("PAIS.IDPAIS"), nullable=False)
    pais = relationship("Pais", back_populates="cuentas")
    idplan = Column("IDPLAN", String(15), ForeignKey("PLAN.IDPLAN"), nullable=True)
    plan = relationship("Plan", back_populates="cuentas")
    password = Column("PASSWORD", String(50), nullable=False)
    identificacion = Column("IDENTIFICACION", String(15), nullable=False)
    nombrecuenta = Column("NOMBRECUENTA", String(150), nullable=False)
    correo = Column("CORREO", String(50), nullable=False)
    telefono = Column("TELEFONO", Integer, nullable=False)
    fecharegistro = Column("FECHAREGISTRO", Date, nullable=False)
    direccion = Column("DIRECCION", String(30))
    tipocuenta = relationship("TipoCuenta", back_populates="cuentas")


class Plan(Base):
    __tablename__ = "PLAN"

    idplan = Column("IDPLAN", String(15), primary_key=True)
    nombreplan = Column("NOMBREPLAN", String(15), nullable=False)
    comision = Column("COMISION", Numeric(2), nullable=False)

    cuentas = relationship("Cuenta", back_populates="plan")

class Pais(Base):
    __tablename__ = "PAIS"

    idpais = Column("IDPAIS", Numeric(3), primary_key=True)
    nombrepais = Column("NOMBREPAIS", String(15), nullable=False)

    cuentas = relationship("Cuenta", back_populates="pais")

class Tarjeta(Base):
    __tablename__ = "TARJETA"

    idtarjeta = Column("IDTARJETA", Integer, primary_key=True, autoincrement=True)
    idtipotarjeta = Column("IDTIPOTARJETA", Numeric(2), nullable=False)
    numerotarjeta = Column("NUMEROTARJETA", Numeric(15), nullable=False)
    ccv = Column("CCV", Numeric(3), nullable=False)
    fechavto = Column("FECHAVTO", Date, nullable=False)

class MetodoPagoCuenta(Base):
    __tablename__ = "METODOPAGOCUENTA"

    idmetodopagocuenta = Column("IDMETODOPAGOCUENTA", String(3), primary_key=True)
    idtarjeta = Column("IDTARJETA", String(15), ForeignKey("TARJETA.IDTARJETA"))
    idcuenta = Column("IDCUENTA", String(15), ForeignKey("CUENTA.IDCUENTA"))
    idtipometodopago = Column("IDTIPOMETODOPAGO", Numeric(2), ForeignKey("TIPOMETODOPAGO.IDTIPOMETODOPAGO"))
    activometodopagocuenta = Column("ACTIVOMETODOPAGOCUENTA", Boolean, nullable=False)

class TipoMetodoPago(Base):
    __tablename__ = "TIPOMETODOPAGO"

    idtipometodopago = Column("IDTIPOMETODOPAGO", Numeric(2), primary_key=True)
    nombretipometodopago = Column("NOMBRETIPOMETODOPAGO", String(15), nullable=False)
