import requests
from bs4 import BeautifulSoup
from fastapi import APIRouter
from api.models import DomainRequest, DomainResponse

router = APIRouter()

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}
BASE_URL = "https://who.is/whois/"

@router.post("/dominios", response_model=DomainResponse)
def verificar_dominio(data: DomainRequest):
    dominio = data.domain
    url = BASE_URL + dominio
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')
    texto = soup.get_text()

    resultado = {
        "domain": dominio,
        "registered": None,
        "expires": None
    }

    if "No WHOIS data was found for" in texto:
        resultado["registered"] = False
        return resultado

    if "The domain" in texto and "is registered" in texto:
        resultado["registered"] = True

    fecha = soup.find("dt", string="Expires")
    if fecha:
        valor = fecha.find_next_sibling("dd")
        if valor:
            resultado["expires"] = valor.text.strip()

    return resultado
