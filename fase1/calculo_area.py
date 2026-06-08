"""
FASE 1 - FarmTech Solutions
Wrapper Python do farmtech_cli.py original para uso no dashboard.
Lógica original mantida: milho=retângulo, soja=círculo.
"""

import math
import subprocess
import sys


def calcular_area(cultura: str, **kwargs) -> dict:
    """
    Calcula área conforme lógica original do farmtech.py:
      - milho: área retangular (base × altura)
      - soja:  área circular (π × raio²)
    """
    cultura = cultura.lower()
    if cultura == "milho":
        base   = kwargs.get("base", 0)
        altura = kwargs.get("altura", 0)
        area_m2 = base * altura
        return {
            "cultura": "milho",
            "tipo": "retangular",
            "base_m": base,
            "altura_m": altura,
            "area_m2": round(area_m2, 2),
            "area_ha": round(area_m2 / 10_000, 4),
        }
    elif cultura == "soja":
        raio    = kwargs.get("raio", 0)
        area_m2 = math.pi * raio ** 2
        return {
            "cultura": "soja",
            "tipo": "circular",
            "raio_m": raio,
            "area_m2": round(area_m2, 2),
            "area_ha": round(area_m2 / 10_000, 4),
        }
    else:
        raise ValueError(f"Cultura inválida: {cultura}. Use 'milho' ou 'soja'.")


def calcular_insumo(insumo_nome: str, quantidade_por_metro: float, metros: int) -> dict:
    """Cálculo de insumos conforme lógica original do farmtech.py."""
    total = quantidade_por_metro * metros
    return {
        "insumo": insumo_nome,
        "quantidade_por_metro": quantidade_por_metro,
        "metros": metros,
        "total": round(total, 2),
    }


def executar_cli():
    """Executa o CLI original (farmtech_cli.py) em subprocess."""
    import os
    cli_path = os.path.join(os.path.dirname(__file__), "farmtech_cli.py")
    subprocess.run([sys.executable, cli_path])


if __name__ == "__main__":
    # Demonstração
    print(calcular_area("milho", base=100, altura=50))
    print(calcular_area("soja", raio=56.4))  # ~10.000 m² ≈ 1 ha
    print(calcular_insumo("fertilizante", 0.5, 1000))
