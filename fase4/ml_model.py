"""
FASE 4 - FarmTech Solutions
Mantém os mesmos modelos e features da Fase 4 original:
  - RandomForestRegressor → umidade_futura
  - RandomForestRegressor → rendimento_t_ha
Features: umidade, temperatura, ph, nitrogenio, fosforo, potassio,
          chuva, volume_irrigacao_L, status_irrigacao_bin
Compatível com os arquivos .pkl já treinados do projeto original.
"""

import os
import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

DATA_DIR   = os.path.join(os.path.dirname(__file__), "..", "data")
CSV_PATH   = os.path.join(DATA_DIR, "dados_agricolas.csv")

# Nomes exatos dos arquivos da Fase 4 original
SCALER_UMIDADE_PATH     = os.path.join(DATA_DIR, "scaler_umidade.pkl")
MODELO_UMIDADE_PATH     = os.path.join(DATA_DIR, "modelo_umidade_futura.pkl")
SCALER_RENDIMENTO_PATH  = os.path.join(DATA_DIR, "scaler_rendimento.pkl")
MODELO_RENDIMENTO_PATH  = os.path.join(DATA_DIR, "modelo_rendimento.pkl")

FEATURES = [
    "umidade", "temperatura", "ph", "nitrogenio",
    "fosforo", "potassio", "chuva", "volume_irrigacao_L",
    "status_irrigacao_bin",
]


def _preparar_df(df: pd.DataFrame) -> pd.DataFrame:
    """Adiciona coluna binária de irrigação se necessário."""
    if "status_irrigacao_bin" not in df.columns and "status_irrigacao" in df.columns:
        df["status_irrigacao_bin"] = df["status_irrigacao"].map(
            {"DESLIGADA": 0, "LIGADA": 1}
        ).fillna(0).astype(int)
    return df


def treinar_modelos(forcar: bool = False) -> dict:
    """
    Treina ambos os regressores e salva os .pkl.
    Se os arquivos já existirem e forcar=False, não retreina.
    """
    os.makedirs(DATA_DIR, exist_ok=True)

    # Gera CSV se não existir
    if not os.path.exists(CSV_PATH):
        from fase3.sensores import salvar_csv
        salvar_csv(300)

    modelos_existem = all(os.path.exists(p) for p in [
        SCALER_UMIDADE_PATH, MODELO_UMIDADE_PATH,
        SCALER_RENDIMENTO_PATH, MODELO_RENDIMENTO_PATH,
    ])
    if modelos_existem and not forcar:
        return {"status": "modelos já existiam (use forcar=True para retreinar)"}

    df = pd.read_csv(CSV_PATH)
    df = _preparar_df(df)

    resultados = {}
    for target, scaler_path, modelo_path in [
        ("umidade_futura",  SCALER_UMIDADE_PATH,    MODELO_UMIDADE_PATH),
        ("rendimento_t_ha", SCALER_RENDIMENTO_PATH,  MODELO_RENDIMENTO_PATH),
    ]:
        X = df[FEATURES]
        y = df[target]
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        scaler = StandardScaler()
        X_train_sc = scaler.fit_transform(X_train)
        X_test_sc  = scaler.transform(X_test)

        modelo = RandomForestRegressor(n_estimators=100, random_state=42, max_depth=8)
        modelo.fit(X_train_sc, y_train)
        y_pred = modelo.predict(X_test_sc)

        mae  = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        r2   = r2_score(y_test, y_pred)

        joblib.dump(scaler, scaler_path)
        joblib.dump(modelo,  modelo_path)

        resultados[target] = {"MAE": round(mae, 4), "RMSE": round(rmse, 4), "R2": round(r2, 4)}

    return resultados


def carregar_modelo_umidade():
    if not os.path.exists(MODELO_UMIDADE_PATH):
        treinar_modelos()
    return joblib.load(SCALER_UMIDADE_PATH), joblib.load(MODELO_UMIDADE_PATH)


def carregar_modelo_rendimento():
    if not os.path.exists(MODELO_RENDIMENTO_PATH):
        treinar_modelos()
    return joblib.load(SCALER_RENDIMENTO_PATH), joblib.load(MODELO_RENDIMENTO_PATH)


def calcular_metricas(df, features, target, scaler, modelo) -> tuple:
    """Mesma assinatura usada no dashboard da Fase 4 original."""
    X = df[features]
    y = df[target]
    _, X_test, _, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    X_sc   = scaler.transform(X_test)
    y_pred = modelo.predict(X_sc)
    mae  = mean_absolute_error(y_test, y_pred)
    mse  = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)
    r2   = r2_score(y_test, y_pred)
    return mae, mse, rmse, r2


if __name__ == "__main__":
    print("Treinando modelos...")
    res = treinar_modelos(forcar=True)
    for k, v in res.items():
        print(f"  {k}: {v}")
