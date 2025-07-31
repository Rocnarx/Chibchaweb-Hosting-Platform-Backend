import json
from fastapi import APIRouter, HTTPException
from pathlib import Path

router_precios = APIRouter()

RUTA_JSON = Path(__file__).resolve().parent.parent.parent / "precios_extensiones.json"

@router_precios.get("/precios-extensiones")
def obtener_precios():
    if not RUTA_JSON.exists():
        raise HTTPException(status_code=404, detail="Archivo de precios no encontrado")

    with open(RUTA_JSON, "r", encoding="utf-8") as archivo:
        data = json.load(archivo)
    return data

@router_precios.put("/precios-extensiones")
def actualizar_precios(nuevos_precios: dict):
    with open(RUTA_JSON, "w", encoding="utf-8") as archivo:
        json.dump(nuevos_precios, archivo, indent=2)

    return {"mensaje": "Precios guardados correctamente"}

