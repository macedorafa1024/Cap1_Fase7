"""
FASE 5 - FarmTech Solutions
Serviço de alertas via Amazon SNS (Simple Notification Service).

Pré-requisitos:
  1. Conta AWS configurada (aws configure ou variáveis de ambiente)
  2. Tópico SNS criado (ver README para instruções)
  3. E-mail inscrito e confirmado no tópico
  4. Variáveis no .env:
       AWS_REGION=us-east-1
       SNS_TOPIC_ARN=arn:aws:sns:us-east-1:XXXX:farmtech-alertas
       ou AWS_SNS_TOPIC_ARN=arn:aws:sns:us-east-1:XXXX:farmtech-alertas
"""

import os
import json
from datetime import datetime

# boto3 é opcional — funciona em modo mock se não estiver instalado
try:
    import boto3
    from botocore.exceptions import ClientError, NoCredentialsError
    BOTO3_DISPONIVEL = True
except ImportError:
    BOTO3_DISPONIVEL = False

from dotenv import load_dotenv

load_dotenv()

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
SNS_TOPIC_ARN = os.getenv("SNS_TOPIC_ARN") or os.getenv("AWS_SNS_TOPIC_ARN", "")

# Limites críticos para acionamento de alertas
LIMITES = {
    "umidade_critica_min": 40,   # % — alerta crítico
    "umidade_alerta_min":  60,   # % — alerta moderado
    "ph_min":              5.5,
    "ph_max":              7.5,
    "temperatura_max":     38,
}


def _get_sns_client():
    if not BOTO3_DISPONIVEL:
        return None
    try:
        return boto3.client("sns", region_name=AWS_REGION)
    except Exception:
        return None


def publicar_alerta_sns(assunto: str, mensagem: str) -> dict:
    """
    Publica mensagem no tópico SNS.
    Se boto3 não estiver disponível ou credenciais ausentes, salva em log local.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    payload = {
        "timestamp": timestamp,
        "assunto": assunto,
        "mensagem": mensagem,
        "fazenda": "FarmTech Solutions - Soja",
    }

    # Tenta publicar no SNS real
    if BOTO3_DISPONIVEL and SNS_TOPIC_ARN:
        client = _get_sns_client()
        if client:
            try:
                response = client.publish(
                    TopicArn=SNS_TOPIC_ARN,
                    Subject=f"[FarmTech] {assunto}"[:100],
                    Message=json.dumps(payload, ensure_ascii=False, indent=2),
                )
                _salvar_log_alerta(payload, enviado=True, message_id=response.get("MessageId"))
                _salvar_alerta_banco(assunto, mensagem, "info", True)
                return {"sucesso": True, "message_id": response.get("MessageId"), "modo": "SNS"}
            except (ClientError, NoCredentialsError) as e:
                _salvar_log_alerta({**payload, "mensagem": f"{mensagem} | Falha SNS: {e}"}, enviado=False)
                _salvar_alerta_banco(assunto, mensagem, "warning", False)
                return {
                    "sucesso": True,
                    "message_id": "MOCK",
                    "modo": "log_local",
                    "payload": payload,
                    "erro": str(e),
                }

    # Modo mock: salva em arquivo local
    _salvar_log_alerta(payload, enviado=False)
    _salvar_alerta_banco(assunto, mensagem, "info", False)
    return {"sucesso": True, "message_id": "MOCK", "modo": "log_local", "payload": payload}


def _salvar_log_alerta(payload: dict, enviado: bool, message_id: str = None):
    """Persiste alerta em arquivo de log local."""
    log_path = os.path.join(os.path.dirname(__file__), "..", "data", "alertas_sns.log")
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    status = "SNS_ENVIADO" if enviado else "LOG_LOCAL"
    linha = f"[{status}] {payload['timestamp']} | {payload['assunto']} | {payload['mensagem']}"
    if message_id:
        linha += f" | MessageId: {message_id}"
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(linha + "\n")


def _salvar_alerta_banco(tipo: str, mensagem: str, severidade: str, enviado_sns: bool) -> None:
    """Registra alertas também na base relacional da Fase 2."""
    try:
        from fase2.database import inserir_alerta

        inserir_alerta(tipo=tipo, mensagem=mensagem, severidade=severidade, enviado_sns=enviado_sns)
    except Exception:
        # O log local continua sendo a fonte de contingência caso o SQLite esteja indisponível.
        pass


def avaliar_e_alertar(leitura: dict) -> list:
    """
    Analisa leitura de sensores e dispara alertas SNS conforme limites.
    Retorna lista de alertas gerados.
    """
    alertas = []
    u = leitura.get("umidade_pct", 100)
    ph = leitura.get("ph", 6.5)
    temp = leitura.get("temperatura_c", 25)

    if u < LIMITES["umidade_critica_min"]:
        msg = (f"ALERTA CRÍTICO: Umidade do solo em {u}% — MUITO ABAIXO do mínimo de "
               f"{LIMITES['umidade_critica_min']}%. Acione irrigação IMEDIATAMENTE.")
        r = publicar_alerta_sns("UMIDADE CRÍTICA", msg)
        alertas.append({"tipo": "umidade_critica", "mensagem": msg, "resultado_sns": r})

    elif u < LIMITES["umidade_alerta_min"]:
        msg = (f"AVISO: Umidade do solo em {u}% — abaixo do ideal ({LIMITES['umidade_alerta_min']}%). "
               f"Verificar necessidade de irrigação.")
        r = publicar_alerta_sns("UMIDADE BAIXA", msg)
        alertas.append({"tipo": "umidade_baixa", "mensagem": msg, "resultado_sns": r})

    if ph < LIMITES["ph_min"]:
        msg = f"ALERTA: pH do solo em {ph} — ÁCIDO. Aplicar calcário. Ideal: {LIMITES['ph_min']}-{LIMITES['ph_max']}."
        r = publicar_alerta_sns("pH ÁCIDO", msg)
        alertas.append({"tipo": "ph_acido", "mensagem": msg, "resultado_sns": r})

    elif ph > LIMITES["ph_max"]:
        msg = f"ALERTA: pH do solo em {ph} — ALCALINO. Verificar calagem. Ideal: {LIMITES['ph_min']}-{LIMITES['ph_max']}."
        r = publicar_alerta_sns("pH ALCALINO", msg)
        alertas.append({"tipo": "ph_alcalino", "mensagem": msg, "resultado_sns": r})

    if temp > LIMITES["temperatura_max"]:
        msg = f"AVISO: Temperatura de {temp}°C — acima do limite ({LIMITES['temperatura_max']}°C). Risco de estresse hídrico."
        r = publicar_alerta_sns("TEMPERATURA ALTA", msg)
        alertas.append({"tipo": "temperatura_alta", "mensagem": msg, "resultado_sns": r})

    return alertas


def alertar_praga(tipo_praga: str, confianca: float, talhao: str = "desconhecido") -> dict:
    """Dispara alerta para detecção de praga pela visão computacional."""
    msg = (f"DETECÇÃO DE PRAGA: {tipo_praga} detectada no {talhao} com "
           f"{confianca:.1%} de confiança. Acionar equipe de manejo fitossanitário.")
    return publicar_alerta_sns("PRAGA DETECTADA", msg)


if __name__ == "__main__":
    print("=== TESTE DE ALERTAS SNS ===")
    leitura_teste = {"umidade_pct": 38, "ph": 5.2, "temperatura_c": 35}
    alertas = avaliar_e_alertar(leitura_teste)
    for a in alertas:
        print(f"  [{a['tipo'].upper()}] {a['mensagem'][:80]}...")
        print(f"   → Modo: {a['resultado_sns'].get('modo')}")
