"""
FASE 6 - FarmTech Solutions
Visão Computacional para detecção de pragas e doenças na soja.
Usa YOLOv8 (ultralytics) se disponível, ou OpenCV + classificador heurístico como fallback.
"""

import os
import random
from datetime import datetime

# Tentativa de importar ultralytics (YOLOv8)
try:
    from ultralytics import YOLO
    YOLO_DISPONIVEL = True
except ImportError:
    YOLO_DISPONIVEL = False

# Tentativa de importar OpenCV
try:
    import cv2
    import numpy as np
    CV2_DISPONIVEL = True
except ImportError:
    CV2_DISPONIVEL = False

CLASSES_PRAGAS = [
    "ferrugem_asiatica",
    "lagarta_da_soja",
    "mosca_branca",
    "percevejo",
    "mancha_alvo",
    "soja_saudavel",
]

MODEL_YOLO_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "yolov8_soja.pt")
IMAGENS_PATH    = os.path.join(os.path.dirname(__file__), "imagens")


def detectar_yolo(imagem_path: str) -> dict:
    """Detecção real com YOLOv8 (requer modelo treinado)."""
    if not YOLO_DISPONIVEL:
        return None
    if not os.path.exists(MODEL_YOLO_PATH):
        return None
    try:
        model = YOLO(MODEL_YOLO_PATH)
        results = model(imagem_path)
        deteccoes = []
        for r in results:
            for box in r.boxes:
                deteccoes.append({
                    "classe": CLASSES_PRAGAS[int(box.cls)] if int(box.cls) < len(CLASSES_PRAGAS) else "desconhecido",
                    "confianca": round(float(box.conf), 3),
                    "bbox": box.xyxy[0].tolist(),
                })
        return {"modo": "YOLOv8", "deteccoes": deteccoes, "imagem": imagem_path}
    except Exception as e:
        return None


def detectar_opencv(imagem_path: str) -> dict:
    """Análise básica com OpenCV (cor, textura) como proxy para triagem."""
    if not CV2_DISPONIVEL or not os.path.exists(imagem_path):
        return None
    try:
        img = cv2.imread(imagem_path)
        if img is None:
            return None
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        # Proporção de pixels amarelados/marrons (indicativo de doença)
        lower_yellow = np.array([15, 50, 50])
        upper_yellow = np.array([35, 255, 255])
        lower_brown  = np.array([5, 50, 20])
        upper_brown  = np.array([20, 255, 200])
        mask_yellow = cv2.inRange(hsv, lower_yellow, upper_yellow)
        mask_brown  = cv2.inRange(hsv, lower_brown, upper_brown)
        total_px = img.shape[0] * img.shape[1]
        prop_doenca = (cv2.countNonZero(mask_yellow) + cv2.countNonZero(mask_brown)) / total_px
        classe = "soja_saudavel" if prop_doenca < 0.15 else "ferrugem_asiatica"
        confianca = min(0.95, 0.5 + prop_doenca * 2)
        return {
            "modo": "OpenCV",
            "deteccoes": [{"classe": classe, "confianca": round(confianca, 3)}],
            "proporcao_pixels_anomalos": round(prop_doenca, 3),
            "imagem": imagem_path,
        }
    except Exception as e:
        return None


def detectar_simulado(imagem_path: str = "simulada") -> dict:
    """Fallback: simulação estocástica para demonstração."""
    random.seed(hash(imagem_path) % 999)
    n = random.randint(0, 3)
    deteccoes = []
    for _ in range(n):
        classe = random.choice(CLASSES_PRAGAS)
        conf = round(random.uniform(0.55, 0.97), 3)
        deteccoes.append({"classe": classe, "confianca": conf})
    # Garante pelo menos soja_saudavel se sem pragas
    if not deteccoes:
        deteccoes.append({"classe": "soja_saudavel", "confianca": 0.95})
    return {"modo": "simulado", "deteccoes": deteccoes, "imagem": imagem_path}


def analisar_imagem(imagem_path: str) -> dict:
    """
    Pipeline de análise:
      1. YOLOv8 (se disponível e modelo carregado)
      2. OpenCV heurístico (se disponível e imagem válida)
      3. Simulação (fallback)
    """
    resultado = detectar_yolo(imagem_path)
    if resultado is None:
        resultado = detectar_opencv(imagem_path)
    if resultado is None:
        resultado = detectar_simulado(imagem_path)

    resultado["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    resultado["pragas_encontradas"] = [
        d for d in resultado["deteccoes"] if d["classe"] != "soja_saudavel"
    ]
    resultado["saudavel"] = len(resultado["pragas_encontradas"]) == 0
    return resultado


def processar_pasta_imagens(pasta: str = None) -> list:
    """Processa todas as imagens de uma pasta."""
    pasta = pasta or IMAGENS_PATH
    extensoes = (".jpg", ".jpeg", ".png", ".bmp")
    resultados = []
    if os.path.isdir(pasta):
        arquivos = [f for f in os.listdir(pasta) if f.lower().endswith(extensoes)]
        for arq in sorted(arquivos):
            caminho = os.path.join(pasta, arq)
            resultado = analisar_imagem(caminho)
            resultados.append(resultado)
    if not resultados:
        # Sem imagens: retorna análises simuladas de demonstração
        for i in range(3):
            resultados.append(analisar_imagem(f"demo_imagem_{i+1}.jpg"))
    return resultados


if __name__ == "__main__":
    print("=== VISÃO COMPUTACIONAL ===")
    resultados = processar_pasta_imagens()
    for r in resultados:
        status = "✓ Saudável" if r["saudavel"] else f"⚠ Pragas: {[d['classe'] for d in r['pragas_encontradas']]}"
        print(f"  {r['imagem']}: {status} [{r['modo']}]")
