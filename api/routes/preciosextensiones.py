import json
from fastapi import APIRouter, HTTPException

router_precios = APIRouter()

RUTA_JSON = "resources/precios.json"

try:
    with open(RUTA_JSON, "r", encoding="utf-8") as archivo:
        data = json.load(archivo)
    EXTENSIONS = list(data.keys())
except Exception as e:
    print("Error cargando extensiones desde precios.json:", e)
    EXTENSIONS = ["com", "net", "org", "co", "io", "app", "info", "dev", "online", "store"]  # fallback mínimo

@router_precios.get("/precios-extensiones")
def obtener_precios():
    if not RUTA_JSON:
        raise HTTPException(status_code=404, detail="Archivo de precios no encontrado")

    with open(RUTA_JSON, "r", encoding="utf-8") as archivo:
        data = json.load(archivo)
    return data

@router_precios.put("/precios-extensiones")
def actualizar_precios(nuevos_precios: dict):
    if not isinstance(nuevos_precios, dict):
        raise HTTPException(status_code=400, detail="Formato inválido: debe ser JSON tipo clave-valor.")

    # Verifica que todos los valores sean números válidos (int o float)
    for key, value in nuevos_precios.items():
        if not isinstance(value, (int, float)):
            raise HTTPException(status_code=400, detail=f"Precio inválido para {key}: debe ser numérico (entero o decimal).")

    with open(RUTA_JSON, "w", encoding="utf-8") as archivo:
        json.dump(nuevos_precios, archivo, indent=2)

    return {"mensaje": "Precios actualizados correctamente"}


