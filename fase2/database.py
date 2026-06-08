"""
FASE 2 - FarmTech Solutions
Banco de dados relacional SQLite com MER/DER para gestão agrícola.

Tabelas:
  - talhoes         : unidades de plantio (talhão)
  - leituras_sensor : histórico de sensores IoT
  - irrigacoes      : registro de eventos de irrigação
  - pragas          : ocorrências detectadas pela visão computacional
  - alertas         : alertas disparados
"""

import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "farmtech.db")


def get_connection() -> sqlite3.Connection:
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(verbose: bool = True):
    """Cria todas as tabelas se não existirem."""
    conn = get_connection()
    cur = conn.cursor()

    cur.executescript("""
        CREATE TABLE IF NOT EXISTS talhoes (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            nome         TEXT    NOT NULL,
            cultura      TEXT    NOT NULL DEFAULT 'Soja',
            comprimento_m REAL   NOT NULL,
            largura_m    REAL    NOT NULL,
            area_ha      REAL    NOT NULL,
            criado_em    TEXT    NOT NULL DEFAULT (datetime('now','localtime'))
        );

        CREATE TABLE IF NOT EXISTS leituras_sensor (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            talhao_id    INTEGER NOT NULL REFERENCES talhoes(id),
            timestamp    TEXT    NOT NULL DEFAULT (datetime('now','localtime')),
            umidade_pct  REAL,
            ph           REAL,
            nitrogenio   REAL,
            fosforo      REAL,
            potassio     REAL,
            temperatura_c REAL,
            precipitacao_mm REAL
        );

        CREATE TABLE IF NOT EXISTS irrigacoes (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            talhao_id    INTEGER NOT NULL REFERENCES talhoes(id),
            timestamp    TEXT    NOT NULL DEFAULT (datetime('now','localtime')),
            duracao_min  REAL    NOT NULL,
            volume_litros REAL,
            motivo       TEXT,
            status       TEXT    NOT NULL DEFAULT 'executada'
        );

        CREATE TABLE IF NOT EXISTS pragas (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            talhao_id    INTEGER REFERENCES talhoes(id),
            timestamp    TEXT    NOT NULL DEFAULT (datetime('now','localtime')),
            tipo_praga   TEXT,
            confianca    REAL,
            imagem_path  TEXT,
            acao_tomada  TEXT
        );

        CREATE TABLE IF NOT EXISTS alertas (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp    TEXT    NOT NULL DEFAULT (datetime('now','localtime')),
            tipo         TEXT    NOT NULL,
            mensagem     TEXT    NOT NULL,
            severidade   TEXT    NOT NULL DEFAULT 'info',
            enviado_sns  INTEGER NOT NULL DEFAULT 0
        );
    """)
    conn.commit()
    conn.close()
    if verbose:
        print(f"[DB] Banco inicializado em: {DB_PATH}")


# ─── CRUD: Talhões ──────────────────────────────────────────────────────────
def inserir_talhao(nome: str, comprimento_m: float, largura_m: float, cultura: str = "Soja") -> int:
    area_ha = (comprimento_m * largura_m) / 10_000
    conn = get_connection()
    cur = conn.execute(
        "INSERT INTO talhoes (nome, cultura, comprimento_m, largura_m, area_ha) VALUES (?,?,?,?,?)",
        (nome, cultura, comprimento_m, largura_m, round(area_ha, 4))
    )
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return new_id


def listar_talhoes() -> list:
    init_db(verbose=False)
    conn = get_connection()
    rows = conn.execute("SELECT * FROM talhoes ORDER BY id").fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ─── CRUD: Leituras de Sensor ───────────────────────────────────────────────
def inserir_leitura(talhao_id: int, umidade: float, ph: float,
                    nitrogenio: float = None, fosforo: float = None,
                    potassio: float = None, temperatura: float = None,
                    precipitacao: float = None) -> int:
    init_db(verbose=False)
    conn = get_connection()
    cur = conn.execute(
        """INSERT INTO leituras_sensor
           (talhao_id, umidade_pct, ph, nitrogenio, fosforo, potassio, temperatura_c, precipitacao_mm)
           VALUES (?,?,?,?,?,?,?,?)""",
        (talhao_id, umidade, ph, nitrogenio, fosforo, potassio, temperatura, precipitacao)
    )
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return new_id


def listar_leituras(talhao_id: int = None, limite: int = 100) -> list:
    init_db(verbose=False)
    conn = get_connection()
    if talhao_id:
        rows = conn.execute(
            "SELECT * FROM leituras_sensor WHERE talhao_id=? ORDER BY timestamp DESC LIMIT ?",
            (talhao_id, limite)
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM leituras_sensor ORDER BY timestamp DESC LIMIT ?", (limite,)
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ─── CRUD: Irrigações ───────────────────────────────────────────────────────
def registrar_irrigacao(talhao_id: int, duracao_min: float, volume_litros: float = None, motivo: str = "") -> int:
    init_db(verbose=False)
    conn = get_connection()
    cur = conn.execute(
        "INSERT INTO irrigacoes (talhao_id, duracao_min, volume_litros, motivo) VALUES (?,?,?,?)",
        (talhao_id, duracao_min, volume_litros, motivo)
    )
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return new_id


def listar_irrigacoes(talhao_id: int = None, limite: int = 50) -> list:
    init_db(verbose=False)
    conn = get_connection()
    q = "SELECT * FROM irrigacoes"
    params = []
    if talhao_id:
        q += " WHERE talhao_id=?"
        params.append(talhao_id)
    q += " ORDER BY timestamp DESC LIMIT ?"
    params.append(limite)
    rows = conn.execute(q, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ─── CRUD: Alertas ──────────────────────────────────────────────────────────
def inserir_alerta(tipo: str, mensagem: str, severidade: str = "info", enviado_sns: bool = False) -> int:
    init_db(verbose=False)
    conn = get_connection()
    cur = conn.execute(
        "INSERT INTO alertas (tipo, mensagem, severidade, enviado_sns) VALUES (?,?,?,?)",
        (tipo, mensagem, severidade, int(enviado_sns))
    )
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return new_id


def listar_alertas(limite: int = 50) -> list:
    init_db(verbose=False)
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM alertas ORDER BY timestamp DESC LIMIT ?", (limite,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def seed_talhoes_padrao() -> None:
    """Garante talhões mínimos para demonstrar o MER/DER na dashboard."""
    init_db(verbose=False)
    if listar_talhoes():
        return
    inserir_talhao("Talhão A", 500, 200, "Soja")
    inserir_talhao("Talhão B", 300, 150, "Milho")


def importar_leituras_csv(csv_path: str, limite: int = 300, limpar: bool = True) -> int:
    """Importa o CSV da Fase 3 para a tabela relacional de leituras."""
    import pandas as pd

    init_db(verbose=False)
    seed_talhoes_padrao()
    talhoes = listar_talhoes()
    if not talhoes:
        return 0

    df = pd.read_csv(csv_path).head(limite)
    conn = get_connection()
    if limpar:
        conn.execute("DELETE FROM leituras_sensor")
        conn.execute("DELETE FROM irrigacoes")

    inseridos = 0
    for idx, row in df.iterrows():
        talhao_id = talhoes[idx % len(talhoes)]["id"]
        conn.execute(
            """INSERT INTO leituras_sensor
               (talhao_id, umidade_pct, ph, nitrogenio, fosforo, potassio, temperatura_c, precipitacao_mm)
               VALUES (?,?,?,?,?,?,?,?)""",
            (
                talhao_id,
                float(row["umidade"]),
                float(row["ph"]),
                float(row["nitrogenio"]),
                float(row["fosforo"]),
                float(row["potassio"]),
                float(row["temperatura"]),
                float(row["chuva"]),
            ),
        )
        if str(row.get("status_irrigacao", "")).upper() == "LIGADA":
            conn.execute(
                "INSERT INTO irrigacoes (talhao_id, duracao_min, volume_litros, motivo) VALUES (?,?,?,?)",
                (
                    talhao_id,
                    20,
                    float(row.get("volume_irrigacao_L", 0)),
                    "Irrigação automática importada do CSV da Fase 3",
                ),
            )
        inseridos += 1

    conn.commit()
    conn.close()
    return inseridos


def estatisticas_banco() -> dict:
    """Retorna indicadores calculados diretamente no SQLite."""
    init_db(verbose=False)
    conn = get_connection()
    row = conn.execute(
        """
        SELECT
            COUNT(*) AS total_leituras,
            AVG(umidade_pct) AS umidade_media,
            AVG(ph) AS ph_medio,
            AVG(temperatura_c) AS temperatura_media,
            AVG(nitrogenio) AS nitrogenio_medio,
            AVG(fosforo) AS fosforo_medio,
            AVG(potassio) AS potassio_medio
        FROM leituras_sensor
        """
    ).fetchone()
    irrigacoes = conn.execute("SELECT COUNT(*) AS total FROM irrigacoes").fetchone()["total"]
    alertas = conn.execute("SELECT COUNT(*) AS total FROM alertas").fetchone()["total"]
    conn.close()
    stats = dict(row)
    stats["total_irrigacoes"] = irrigacoes
    stats["total_alertas"] = alertas
    return stats


if __name__ == "__main__":
    init_db()
    # Seed de exemplo
    if not listar_talhoes():
        inserir_talhao("Talhão A", 500, 200)
        inserir_talhao("Talhão B", 300, 150)
        print("[DB] Talhões de exemplo inseridos.")
    print("[DB] Talhões:", listar_talhoes())
