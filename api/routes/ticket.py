from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from datetime import date
from api.DAO.database import SessionLocal
from api.ORM.models_sqlalchemy import Ticket, Cuenta
from api.DTO.models import CrearTicketRequest, RespuestaTicketRequest, CambiarEstadoTicketRequest, CambiarNivelTicketRequest, AsignarTicketRequest
from api.AIGEN.AI_utils import clasificar_correo, generar_respuesta_correo, enviar_email, guardar_ticket_json, agregar_respuesta_a_historial
import glob
import os
import json
router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/CrearTicket")
def crear_ticket(data: CrearTicketRequest, db: Session = Depends(get_db)):
    cuenta = db.query(Cuenta).filter_by(IDCUENTA=data.idcliente).first()
    if not cuenta:
        raise HTTPException(status_code=404, detail="Cuenta no encontrada")

    modelo = "openrouter/horizon-beta"
    categoria = clasificar_correo(data.descrip_ticket, modelo)

    nuevo_ticket = Ticket(
        IDCLIENTE=data.idcliente,
        DESCRTICKET=data.descrip_ticket,
        NIVEL=1,
        FCHCREACION=date.today(),
        ESTADOTICKET=1,
        FCHSOLUCION=None,
        IDEMPLEADO=None
    )

    db.add(nuevo_ticket)
    db.commit()
    db.refresh(nuevo_ticket)

    ticket_id = f"TK{nuevo_ticket.IDTICKET:05d}"

    respuesta_ia = generar_respuesta_correo(
        correo_entrada=data.descrip_ticket,
        modelo=modelo,
        num_ticket=ticket_id,
        nombre_cliente=cuenta.NOMBRECUENTA
    )

    enviado = enviar_email(
        destinatario=cuenta.CORREO,
        asunto=f"Confirmación de Ticket {ticket_id} – ChibchaWeb",
        cuerpo=respuesta_ia
    )

    if not enviado:
        raise HTTPException(status_code=500, detail="Error al enviar el correo al cliente")

    # Construir el JSON para guardar
    data_json = {
        "codigo": ticket_id,
        "id_ticket": nuevo_ticket.IDTICKET,
        "id_cliente": cuenta.IDCUENTA,
        "nombre_cliente": cuenta.NOMBRECUENTA,
        "descripcion": nuevo_ticket.DESCRTICKET,
        "fecha_creacion": str(nuevo_ticket.FCHCREACION),
        "estado": nuevo_ticket.ESTADOTICKET,
        "nivel": nuevo_ticket.NIVEL,
        "categoria": categoria,
        "correo_cliente": cuenta.CORREO,
        "respuesta": respuesta_ia
    }

    # Guardar el JSON en disco
    guardar_ticket_json(ticket_id, data_json)

    return {
        "mensaje": "Ticket creado correctamente",
        "ticket": data_json
    }

@router.post("/ticket/{codigo}/respuesta")
def agregar_respuesta_ticket(codigo: str, datos: RespuestaTicketRequest):
    try:
        nueva_entrada = agregar_respuesta_a_historial(
            ticket_id=codigo,
            mensaje=datos.mensaje,
            autor=datos.autor
        )
        return {
            "mensaje": f"Respuesta agregada al historial del ticket {codigo}",
            "entrada": nueva_entrada
        }
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al actualizar el historial: {str(e)}")

@router.get("/consultarTicketporIDCUENTA")
def consultar_tickets_por_idcuenta(idcuenta: str = Query(...)):
    ruta = "tickets_json"
    coincidencias = []

    for file_path in glob.glob(f"{ruta}/TK*.json"):
        with open(file_path, "r", encoding="utf-8") as f:
            ticket_data = json.load(f)
            if ticket_data.get("id_cliente") == idcuenta:
                coincidencias.append(ticket_data)

    if not coincidencias:
        raise HTTPException(status_code=404, detail="No se encontraron tickets para esta cuenta")

    return {"tickets": coincidencias}

@router.patch("/CambiarNivelTicket/{codigo}")
def cambiar_nivel_ticket(codigo: str, data: CambiarNivelTicketRequest):
    ruta = os.path.join("tickets_json", f"{codigo}.json")
    if not os.path.exists(ruta):
        raise HTTPException(status_code=404, detail="Ticket no encontrado")

    with open(ruta, "r", encoding="utf-8") as f:
        ticket = json.load(f)

    ticket["nivel"] = data.nivel

    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(ticket, f, ensure_ascii=False, indent=4)

    return {"mensaje": f"Nivel del ticket {codigo} actualizado a {data.nivel}"}

@router.patch("/CambiarEstadoTicket/{codigo}")
def cambiar_estado_ticket(codigo: str, data: CambiarEstadoTicketRequest):
    ruta = os.path.join("tickets_json", f"{codigo}.json")
    if not os.path.exists(ruta):
        raise HTTPException(status_code=404, detail="Ticket no encontrado")

    with open(ruta, "r", encoding="utf-8") as f:
        ticket = json.load(f)

    ticket["estado"] = data.estado

    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(ticket, f, ensure_ascii=False, indent=4)

    return {"mensaje": f"Estado del ticket {codigo} actualizado a {data.estado}"}

@router.patch("/asignarTicket/{codigo}")
def asignar_ticket(codigo: str, data: AsignarTicketRequest):
    ruta = os.path.join("tickets_json", f"{codigo}.json")
    if not os.path.exists(ruta):
        raise HTTPException(status_code=404, detail="Ticket no encontrado")

    with open(ruta, "r", encoding="utf-8") as f:
        ticket = json.load(f)

    ticket["idempleado"] = data.idempleado

    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(ticket, f, ensure_ascii=False, indent=4)

    return {"mensaje": f"Ticket {codigo} asignado al empleado {data.idempleado}"}

@router.get("/ticket/{codigo}")
def obtener_ticket_por_codigo(codigo: str):
    ruta = os.path.join("tickets_json", f"{codigo}.json")
    if not os.path.exists(ruta):
        raise HTTPException(status_code=404, detail="Ticket no encontrado")

    with open(ruta, "r", encoding="utf-8") as f:
        ticket = json.load(f)

    return ticket

@router.get("/ver-tickets")
def ver_tickets_por_estado(estado_ticket: int = Query(...), db: Session = Depends(get_db)):
    tickets = db.query(Ticket)\
    .filter(Ticket.ESTADOTICKET == estado_ticket).all()


    if not tickets:
        raise HTTPException(status_code=404, detail="No se encontraron tickets con ese estado")

    resultados = []
    for t in tickets:
        cliente = db.query(Cuenta).filter_by(IDCUENTA=t.IDCLIENTE).first()
        empleado = db.query(Cuenta).filter_by(IDCUENTA=t.IDEMPLEADO).first() if t.IDEMPLEADO else None

        resultados.append({
            "idticket": t.IDTICKET,
            "descripcion": t.DESCRTICKET,
            "nivel": t.NIVEL,
            "fecha_creacion": t.FCHCREACION,
            "estado_ticket": t.ESTADOTICKET,
            "fecha_solucion": t.FCHSOLUCION,
            "cliente": {
                "id": cliente.IDCUENTA,
                "nombre": cliente.NOMBRECUENTA,
                "correo": cliente.CORREO
            },
            "empleado_asignado": {
                "id": empleado.IDCUENTA,
                "nombre": empleado.NOMBRECUENTA,
                "correo": empleado.CORREO
            } if empleado else None
        })

    return resultados

@router.get("/ver-tickets-niveles")
def ver_tickets_por_estado_y_nivel(
    estado_ticket: int = Query(...),
    nivel_ticket: int = Query(...),
    db: Session = Depends(get_db)
):
    tickets = db.query(Ticket)\
        .filter(
            Ticket.ESTADOTICKET == estado_ticket,
            Ticket.NIVEL == nivel_ticket
        ).all()

    if not tickets:
        raise HTTPException(status_code=404, detail="No se encontraron tickets con ese estado y nivel")

    resultados = []
    for t in tickets:
        cliente = db.query(Cuenta).filter_by(IDCUENTA=t.IDCLIENTE).first()
        empleado = db.query(Cuenta).filter_by(IDCUENTA=t.IDEMPLEADO).first() if t.IDEMPLEADO else None

        resultados.append({
            "idticket": t.IDTICKET,
            "descripcion": t.DESCRTICKET,
            "nivel": t.NIVEL,
            "fecha_creacion": t.FCHCREACION,
            "estado_ticket": t.ESTADOTICKET,
            "fecha_solucion": t.FCHSOLUCION,
            "cliente": {
                "id": cliente.IDCUENTA,
                "nombre": cliente.NOMBRECUENTA,
                "correo": cliente.CORREO
            },
            "empleado_asignado": {
                "id": empleado.IDCUENTA,
                "nombre": empleado.NOMBRECUENTA,
                "correo": empleado.CORREO
            } if empleado else None
        })

    return resultados