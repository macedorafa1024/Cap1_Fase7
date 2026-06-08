"""
FASE 1 - FarmTech Solutions
API Meteorológica OpenWeatherMap.
"""

import os

import requests
from dotenv import load_dotenv

load_dotenv()

OWM_API_KEY = os.getenv("OPENWEATHER_API_KEY", "").strip()
OWM_URL = "https://api.openweathermap.org/data/2.5/weather"


def buscar_clima(cidade: str = "Sao Paulo", pais: str = "BR") -> dict:
    """
    Consulta OpenWeatherMap.
    Retorna descrição, temperatura, umidade e velocidade do vento.
    Se a chave não estiver configurada, usa dados simulados para não travar a dashboard.
    """
    if not OWM_API_KEY:
        return {
            "cidade": cidade,
            "descricao": "céu limpo (simulado)",
            "temperatura_c": 28.0,
            "umidade_relativa_pct": 65,
            "vento_ms": 3.5,
            "sucesso": False,
            "erro": "OPENWEATHER_API_KEY não configurada no .env",
        }

    params = {
        "q": f"{cidade},{pais}",
        "appid": OWM_API_KEY,
        "units": "metric",
        "lang": "pt",
    }
    try:
        resp = requests.get(OWM_URL, params=params, timeout=10)
        resp.raise_for_status()
        dados = resp.json()
        return {
            "cidade": cidade,
            "descricao": dados["weather"][0]["description"],
            "temperatura_c": dados["main"]["temp"],
            "umidade_relativa_pct": dados["main"]["humidity"],
            "vento_ms": dados["wind"]["speed"],
            "sucesso": True,
        }
    except Exception as e:
        # Fallback com dados simulados (sem travar o dashboard)
        return {
            "cidade": cidade,
            "descricao": "céu limpo (simulado)",
            "temperatura_c": 28.0,
            "umidade_relativa_pct": 65,
            "vento_ms": 3.5,
            "sucesso": False,
            "erro": str(e),
        }


if __name__ == "__main__":
    clima = buscar_clima("Sao Paulo")
    print("Descrição do clima:", clima["descricao"])
    print("Temperatura atual:", clima["temperatura_c"], "°C")
    print("Umidade:",           clima["umidade_relativa_pct"], "%")
    print("Velocidade do vento:", clima["vento_ms"], "m/s")
