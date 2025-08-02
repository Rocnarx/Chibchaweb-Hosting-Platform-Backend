from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from api.DAO.database import SessionLocal
from api.ORM.models_sqlalchemy import Factura, Cuenta, Carrito, CarritoDominio, Dominio, Plan
import smtplib
from email.message import EmailMessage
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from io import BytesIO
from decimal import Decimal
import os
from reportlab.lib.utils import ImageReader

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/ObtenerFacturas")
def obtener_facturas(idcuenta: str, db: Session = Depends(get_db)):
    try:
        # Consultar todos los carritos asociados a la cuenta
        carritos = db.query(Carrito).filter_by(IDCUENTA=idcuenta).all()

        if not carritos:
            raise HTTPException(status_code=404, detail="No se encontraron carritos para esta cuenta")

        # Consultar las facturas asociadas a esos carritos
        facturas = db.query(Factura).filter(Factura.IDCARRITO.in_([carrito.IDCARRITO for carrito in carritos])).all()

        if not facturas:
            raise HTTPException(status_code=404, detail="No se encontraron facturas para esta cuenta")

        # Preparar el diccionario con las facturas
        facturas_dict = [
            {
                "idfactura": factura.IDFACTURA,
                "pago_factura": factura.PAGOFACTURA,
                "vig_factura": factura.VIGFACTURA
            }
            for factura in facturas
        ]

        return {"facturas": facturas_dict}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener las facturas: {str(e)}")




def generar_factura_pdf(data: dict) -> bytes:
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    try:
        logo_path = "resources\logo.png"
        logo = ImageReader(logo_path)

        # Calcular dimensiones conservando proporción
        iw, ih = logo.getSize()
        logo_width = 100  # ancho fijo en puntos
        logo_height = int((ih / iw) * logo_width)

        x = width - logo_width - 50  # margen derecho
        y = height - logo_height - 40  # margen superior

        c.drawImage(logo, x, y, width=logo_width, height=logo_height, mask='auto')
    except Exception as e:
        print(f"[!] Error cargando el logo: {e}")

    c.setFont("Helvetica-Bold", 16)
    c.drawString(180, 750, "Factura de Venta - CHIBCHAWEB")
    c.setFont("Helvetica", 12)
    c.drawString(50, 710, f"Cliente: {data['nombre_cliente']} ({data['identificacion_cliente']})")
    c.drawString(50, 690, f"Correo: {data['correo_cliente']}")
    c.drawString(50, 670, f"Fecha de pago: {data['fecha_pago']}")
    c.drawString(50, 650, f"Vigencia hasta: {data['vigencia']}")

    c.drawString(50, 620, "Dominios comprados:")
    y = 600
    for dom in data["dominios"]:
        c.drawString(70, y, f"- {dom['dominio']} | ${dom['precio']:.2f}")
        y -= 20

    c.drawString(50, y-10, f"Subtotal: ${data['total_sin_descuento']:.2f}")
    c.drawString(50, y-30, f"Comisión aplicada: {data['comision_aplicada']}%")
    c.drawString(50, y-50, f"Descuento por comisión: ${data['descuento_comision']:.2f}")
    c.drawString(50, y-70, f"Total pagado: ${data['total_pagado']:.2f}")

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer.read()




@router.get("/EnviarFactura/{idfactura}")
def enviar_factura(idfactura: int, db: Session = Depends(get_db)):
    factura = db.query(Factura).filter(Factura.IDFACTURA == idfactura).first()
    if not factura:
        raise HTTPException(status_code=404, detail="Factura no encontrada")

    carrito = factura.carrito
    cuenta = db.query(Cuenta).filter(Cuenta.IDCUENTA == carrito.IDCUENTA).first()
    if not cuenta:
        raise HTTPException(status_code=404, detail="Cuenta no encontrada")

    dominios_carrito = db.query(CarritoDominio).filter(CarritoDominio.IDCARRITO == carrito.IDCARRITO).all()
    dominios = []
    total = Decimal(0)

    for cd in dominios_carrito:
        dominio = db.query(Dominio).filter(Dominio.IDDOMINIO == cd.IDDOMINIO).first()
        if dominio:
            dominios.append({
                "dominio": dominio.NOMBREPAGINA,
                "precio": float(dominio.PRECIODOMINIO)
            })
            total += dominio.PRECIODOMINIO

    plan = cuenta.PLAN_REL
    comision = plan.COMISION if plan else Decimal(0)
    descuento = (total * comision / Decimal(100)).quantize(Decimal("0.01"))
    total_final = (total - descuento).quantize(Decimal("0.01"))

    data = {
        "nombre_cliente": cuenta.NOMBRECUENTA,
        "correo_cliente": cuenta.CORREO,
        "identificacion_cliente": cuenta.IDENTIFICACION,
        "fecha_pago": factura.PAGOFACTURA.strftime("%Y-%m-%d"),
        "vigencia": factura.VIGFACTURA.strftime("%Y-%m-%d"),
        "dominios": dominios,
        "total_sin_descuento": float(total),
        "comision_aplicada": float(comision),
        "descuento_comision": float(descuento),
        "total_pagado": float(total_final)
    }

    # Generar PDF
    pdf_content = generar_factura_pdf(data)

    # Configuración del correo
    remitente = os.getenv("EMAIL_REMITENTE")
    destinatario = cuenta.CORREO
    contraseña = os.getenv("EMAIL_CONTRASENA")  # usa un .env o variable de entorno real

    msg = EmailMessage()
    msg["Subject"] = "Factura de Venta CHIBCHAWEB"
    msg["From"] = remitente
    msg["To"] = destinatario
    msg.set_content(f"""
Hola {cuenta.NOMBRECUENTA},

Adjunto encontrarás tu factura por la compra de dominios en ChibchaWeb.

Gracias por tu preferencia.

— Equipo ChibchaWeb
""")
    msg.add_attachment(pdf_content, maintype="application", subtype="pdf", filename="Factura_ChibchaWeb.pdf")

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(remitente, contraseña)
            smtp.send_message(msg)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al enviar el correo: {str(e)}")

    return {"mensaje": f"Factura enviada exitosamente a {cuenta.CORREO}"}