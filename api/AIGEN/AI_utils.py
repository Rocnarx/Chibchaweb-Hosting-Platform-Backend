from openai import OpenAI
import os
from dotenv import load_dotenv
from email.message import EmailMessage
import smtplib
import json
from datetime import datetime
load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

EMAIL_USER = os.getenv("EMAIL_REMITENTE")
EMAIL_PASS = os.getenv("EMAIL_CONTRASENA")

def guardar_ticket_json(ticket_id: str, data: dict, ruta="tickets_json"):
    os.makedirs(ruta, exist_ok=True)
    path = os.path.join(ruta, f"{ticket_id}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def generar_respuesta_correo(correo_entrada, modelo: str, num_ticket: str, nombre_cliente: str):
    prompt = f"""
Acabas de recibir un mensaje de soporte técnico de un cliente llamado {nombre_cliente}, de la empresa ChibchaWeb. Tu tarea es redactar un correo de respuesta automática cordial y personalizada que cumpla con lo siguiente:

- Salude directamente al cliente por su nombre (ej. "Hola {nombre_cliente},").
- Confirme que hemos recibido su solicitud.
- Mencione claramente el número de ticket generado: {num_ticket}.
- Agradezca por contactarnos.
- Exprese empatía.
- Incluya una intención de solución muy básica, como una posible causa general o que el equipo ya está revisando el área relacionada. No des una solución técnica ni promesas específicas.
- Indique el tiempo estimado de respuesta (24 a 48 horas).
- Termine con una despedida amable.

Usa un tono humano, profesional y cercano, evitando sonar genérico o robotizado.

Mensaje original del cliente:
\"\"\" 
{correo_entrada}
\"\"\"

Ahora redacta el correo de respuesta:
"""

    chat_response = client.chat.completions.create(
        model=modelo,
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=1.2
    )

    return chat_response.choices[0].message.content.strip()


def clasificar_correo(correo_entrada: str, modelo: str):
    prompt = f"""
Tu tarea es clasificar correos electrónicos según su intención principal.

Categorías posibles (elige SOLO una):
- cancelación
- reclamo
- consulta
- agradecimiento
- solicitud
- otra

Correo recibido:
\"\"\"
{correo_entrada}
\"\"\"

Responde SOLO con la categoría correspondiente, sin explicaciones adicionales.
    """

    chat_response = client.chat.completions.create(
        model=modelo,
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )

    return chat_response.choices[0].message.content.strip()

def enviar_email(destinatario, asunto, cuerpo):
    msg = EmailMessage()
    msg["Subject"] = asunto
    msg["From"] = EMAIL_USER
    msg["To"] = destinatario
    msg.set_content(cuerpo)

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(EMAIL_USER, EMAIL_PASS)
            smtp.send_message(msg)
        return True
    except Exception as e:
        print("❌ Error al enviar:", e)
        return False

def agregar_respuesta_a_historial(ticket_id: str, mensaje: str, autor: str):
    path = os.path.join("tickets_json", f"{ticket_id}.json")
    if not os.path.exists(path):
        raise FileNotFoundError(f"No se encontró el historial del ticket {ticket_id}")

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    nueva_respuesta = {
        "autor": autor,
        "mensaje": mensaje,
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M")
    }

    if "historial" not in data:
        data["historial"] = []

    data["historial"].append(nueva_respuesta)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    return nueva_respuesta
    
def generar_dominios_desde_descripcion(descripcion: str, modelo: str = "openrouter/horizon-beta") -> list[str]:
    prompt = f"""
Genera 10 nombres de dominio únicos, creativos y disponibles para un negocio descrito como:

"{descripcion}"

Requisitos:
- Solo incluye el nombre (sin www. ni https).
- Todos deben estar en formato .com
- Evita usar caracteres especiales o espacios.
- Haz que suenen profesionales, fáciles de recordar y relacionados al negocio.
- No expliques, solo devuelve la lista (uno por línea).
    """

    response = client.chat.completions.create(
        model=modelo,
        messages=[{"role": "user", "content": prompt}],
        temperature=1.1
    )

    texto = response.choices[0].message.content.strip()
    # Separa por líneas, limpia vacíos y devuelve lista
    dominios = [line.strip().lower() for line in texto.splitlines() if line.strip()]
    return dominios