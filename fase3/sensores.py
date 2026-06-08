"""
FASE 3 - FarmTech Solutions
Gera dados de sensores com EXATAMENTE as mesmas colunas usadas na Fase 4:
  umidade, temperatura, ph, nitrogenio, fosforo, potassio,
  chuva, volume_irrigacao_L, status_irrigacao,
  umidade_futura, rendimento_t_ha
Baseado em gerar_sensores_fase2.py do Cap1_Fase3.
"""

import random
import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta

CSV_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "dados_agricolas.csv")


def simular_leitura() -> dict:
    """Simula uma leitura do ESP32 (DHT22 + LDR + nutrientes)."""
    umidade     = round(random.uniform(20, 90), 2)
    temperatura = round(random.uniform(18, 38), 2)
    ph          = round(random.uniform(5.0, 8.0), 2)
    nitrogenio  = round(random.uniform(10, 80), 2)
    fosforo     = round(random.uniform(5, 60), 2)
    potassio    = round(random.uniform(10, 70), 2)
    chuva       = round(random.uniform(0, 30), 2)
    volume_irrig = round(random.uniform(0, 500), 2)
    status      = random.choice(["LIGADA", "DESLIGADA"])

    # Umidade futura: regra baseada nas condições
    umidade_futura = umidade + (chuva * 0.3) + (volume_irrig * 0.05) - (temperatura * 0.2)
    umidade_futura = round(max(10, min(100, umidade_futura)), 2)

    # Rendimento t/ha: influenciado por N, P, K, umidade e pH
    rendimento = (
        0.05 * nitrogenio +
        0.03 * fosforo +
        0.03 * potassio +
        0.02 * umidade -
        abs(ph - 6.5) * 0.3 +
        random.gauss(2, 0.5)
    )
    rendimento = round(max(0.5, min(8.0, rendimento)), 2)

    return {
        "umidade":            umidade,
        "temperatura":        temperatura,
        "ph":                 ph,
        "nitrogenio":         nitrogenio,
        "fosforo":            fosforo,
        "potassio":           potassio,
        "chuva":              chuva,
        "volume_irrigacao_L": volume_irrig,
        "status_irrigacao":   status,
        "umidade_futura":     umidade_futura,
        "rendimento_t_ha":    rendimento,
    }


def gerar_dataset(n: int = 300) -> pd.DataFrame:
    """Gera N registros — equivale ao gerar_sensores_fase2.py original."""
    random.seed(42)
    np.random.seed(42)
    registros = [simular_leitura() for _ in range(n)]
    return pd.DataFrame(registros)


def salvar_csv(n: int = 300, forcar: bool = False) -> str:
    """Salva o CSV em data/dados_agricolas.csv (só recria se não existir ou forcar=True)."""
    os.makedirs(os.path.dirname(CSV_PATH), exist_ok=True)
    if not os.path.exists(CSV_PATH) or forcar:
        df = gerar_dataset(n)
        df.to_csv(CSV_PATH, index=False)
        print(f"[Fase3] CSV salvo: {CSV_PATH} ({len(df)} registros)")
    return CSV_PATH


def verificar_irrigacao(leitura: dict) -> dict:
    """Lógica de ativação da bomba (baseada nas regras do projeto original)."""
    irrigar = (
        leitura["umidade"] < 40 and
        leitura["chuva"] < 5
    )
    return {
        **leitura,
        "irrigar": irrigar,
        "status_irrigacao": "LIGADA" if irrigar else "DESLIGADA",
    }


if __name__ == "__main__":
    salvar_csv(300, forcar=True)
    print("Exemplo de leitura:", simular_leitura())
