import json
from fastapi import APIRouter, HTTPException, Body, Query
from typing import Dict

router = APIRouter()

RUTA_JSON = "resources/traslations.json"

# Cargar el archivo de traducción
def load_translations():
    with open(RUTA_JSON, "r") as file:
        return json.load(file)

translations = load_translations()

# Guardar las traducciones modificadas
def save_translations(data: Dict):
    with open(RUTA_JSON, "w") as file:
        json.dump(data, file, indent=4)

@router.post("/updateTranslations")
def update_translations(translations: Dict[str, Dict[str, str]] = Body(...)):
    try:
        # Cargar las traducciones actuales
        current_translations = load_translations()

        # Iterar sobre las traducciones recibidas y agregarlas/actualizarlas en el diccionario actual
        for lang, lang_translations in translations.items():
            if lang not in current_translations:
                current_translations[lang] = {}  # Si no existe, inicializarlo como un diccionario vacío
            # Agregar/actualizar las traducciones para cada idioma
            current_translations[lang].update(lang_translations)

        # Guardar las traducciones actualizadas en el archivo JSON
        save_translations(current_translations)

        return {"message": "Translations updated successfully!"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating translations: {str(e)}")


@router.get("/translate")
def translate(key: str, lang: str = Query("en", min_length=2, max_length=2)):
    # Validar el idioma solicitado
    if lang not in translations:
        raise HTTPException(status_code=400, detail="Invalid language code")

    # Verificar si la clave de traducción existe
    if key not in translations[lang]:
        raise HTTPException(status_code=404, detail="Translation key not found")

    # Devolver la traducción
    return { "translation": translations[lang][key] }