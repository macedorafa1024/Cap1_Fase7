"""
FASE 7 - FarmTech Solutions
Dashboard integrado — expande o dashboard original da Fase 4 com todas as fases.
Executar: streamlit run main_dashboard.py
"""

import sys, os
os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib")
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px

# ─── Imports das fases ────────────────────────────────────────────────────────
from fase1.calculo_area      import calcular_area, calcular_insumo
from fase1.api_meteorologica import buscar_clima
from fase2.database          import (
    DB_PATH,
    estatisticas_banco,
    importar_leituras_csv,
    init_db,
    listar_alertas,
    listar_irrigacoes,
    listar_leituras,
    listar_talhoes,
    seed_talhoes_padrao,
)
from fase3.sensores          import simular_leitura, salvar_csv, verificar_irrigacao, CSV_PATH
from fase4.ml_model          import (
    carregar_modelo_umidade, carregar_modelo_rendimento,
    calcular_metricas, treinar_modelos, FEATURES
)
from fase5.alertas_sns       import avaliar_e_alertar, alertar_praga, publicar_alerta_sns

# ─── Página ───────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="FarmTech Solutions | Dashboard",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
.main-header{font-size:2rem;font-weight:700;color:#2d6a4f;border-bottom:3px solid #52b788;padding-bottom:.5rem}
.fase-tag{background:#52b788;color:#fff;padding:2px 10px;border-radius:12px;font-size:.75rem;font-weight:600}
</style>""", unsafe_allow_html=True)


# ─── Garantir CSV e modelos na inicialização ──────────────────────────────────
@st.cache_resource
def inicializar():
    salvar_csv(300)          # cria dados_agricolas.csv se não existir
    treinar_modelos()        # cria .pkl se não existirem
    init_db(verbose=False)    # cria banco relacional da Fase 2
    seed_talhoes_padrao()
    if not estatisticas_banco()["total_leituras"]:
        importar_leituras_csv(CSV_PATH, limite=300, limpar=True)
    return True

inicializar()


# ─── Funções de cache (mantidas do dashboard original da Fase 4) ──────────────
@st.cache_data
def carregar_dados():
    df = pd.read_csv(CSV_PATH)
    if "status_irrigacao_bin" not in df.columns and "status_irrigacao" in df.columns:
        df["status_irrigacao_bin"] = df["status_irrigacao"].map(
            {"DESLIGADA": 0, "LIGADA": 1}
        ).fillna(0).astype(int)
    return df

@st.cache_resource
def _modelo_umidade():
    return carregar_modelo_umidade()

@st.cache_resource
def _modelo_rendimento():
    return carregar_modelo_rendimento()

def status_to_bin(s):
    return 1 if s == "LIGADA" else 0


# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🌾 FarmTech Solutions")
    st.markdown("**Gestão Agrícola Inteligente**")
    st.divider()
    pagina = st.radio("📑 Navegação", [
        "🏠 Visão Geral",
        "🌤️ Fase 1 – Área & Clima",
        "🗄️ Fase 2 – Banco de Dados",
        "📡 Fase 3 – Sensores IoT",
        "🤖 Fase 4 – Machine Learning",
        "☁️ Fase 5 – Alertas AWS",
        "👁️ Fase 6 – Visão Computacional",
    ])
    st.divider()
    st.caption("FIAP — 1TIAO | Fase 7 | RM566955")


# ════════════════════════════════════════════════════════════════════════════════
# VISÃO GERAL
# ════════════════════════════════════════════════════════════════════════════════
if pagina == "🏠 Visão Geral":
    st.markdown('<p class="main-header">🌱 FarmTech Solutions — Dashboard Integrado</p>', unsafe_allow_html=True)
    st.caption("Fases 1 → 7 integradas em um único sistema")

    df = carregar_dados()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📊 Registros no dataset", len(df))
    c2.metric("💧 Umidade média (%)", f"{df['umidade'].mean():.1f}")
    c3.metric("🌾 Rendimento médio (t/ha)", f"{df['rendimento_t_ha'].mean():.2f}")
    c4.metric("🚿 Irrigações LIGADAS", int((df["status_irrigacao"] == "LIGADA").sum()))

    st.divider()
    fig = px.histogram(df, x="umidade", nbins=30, title="Distribuição de Umidade",
                       color_discrete_sequence=["#52b788"])
    st.plotly_chart(fig, width="stretch")

    col1, col2 = st.columns(2)
    with col1:
        fig2 = px.scatter(df, x="umidade", y="rendimento_t_ha", color="status_irrigacao",
                          title="Umidade × Rendimento", opacity=0.6)
        st.plotly_chart(fig2, width="stretch")
    with col2:
        fig3 = px.box(df, y="rendimento_t_ha", color="status_irrigacao",
                      title="Rendimento por Status de Irrigação")
        st.plotly_chart(fig3, width="stretch")


# ════════════════════════════════════════════════════════════════════════════════
# FASE 1 – ÁREA & CLIMA
# ════════════════════════════════════════════════════════════════════════════════
elif pagina == "🌤️ Fase 1 – Área & Clima":
    st.markdown('<p class="main-header">🌤️ Fase 1 — Área de Plantio & Clima</p>', unsafe_allow_html=True)

    tab_area, tab_clima, tab_r = st.tabs(["📐 Cálculo de Área", "🌦️ Clima (OpenWeatherMap)", "📊 Análise R"])

    with tab_area:
        st.subheader("Calculadora original do farmtech.py")
        cultura = st.selectbox("Cultura", ["milho", "soja"])
        if cultura == "milho":
            c1, c2 = st.columns(2)
            base   = c1.number_input("Base (m)", 10.0, 5000.0, 100.0)
            altura = c2.number_input("Altura (m)", 10.0, 5000.0, 50.0)
            if st.button("Calcular", type="primary"):
                res = calcular_area("milho", base=base, altura=altura)
                st.success(f"Área de plantio de milho: **{res['area_m2']:.2f} m² ({res['area_ha']:.4f} ha)**")
        else:
            raio = st.number_input("Raio (m)", 10.0, 2000.0, 56.4)
            if st.button("Calcular", type="primary"):
                res = calcular_area("soja", raio=raio)
                st.success(f"Área de plantio de soja: **{res['area_m2']:.2f} m² ({res['area_ha']:.4f} ha)**")

        st.divider()
        st.subheader("Cálculo de Insumos")
        c1, c2, c3 = st.columns(3)
        insumo_nome = c1.text_input("Insumo", "fertilizante")
        qtd_metro   = c2.number_input("Qtd/metro (L ou kg)", 0.1, 100.0, 0.5)
        metros      = c3.number_input("Metros da lavoura", 1, 100000, 1000)
        if st.button("Calcular Insumo"):
            res_i = calcular_insumo(insumo_nome, qtd_metro, int(metros))
            st.info(f"Necessário: **{res_i['total']:.2f} unidades** de {insumo_nome}")

    with tab_clima:
        st.subheader("API OpenWeatherMap (farmtech_api.R)")
        cidade = st.text_input("Cidade", "Sao Paulo")
        if st.button("🌤️ Buscar Clima", type="primary"):
            with st.spinner("Consultando OpenWeatherMap..."):
                clima = buscar_clima(cidade)
            if clima["sucesso"]:
                st.success(f"✅ Dados obtidos para **{clima['cidade']}**")
            else:
                st.warning("⚠️ API indisponível — dados simulados")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("🌡️ Temperatura", f"{clima['temperatura_c']} °C")
            c2.metric("💧 Umidade",      f"{clima['umidade_relativa_pct']} %")
            c3.metric("💨 Vento",         f"{clima['vento_ms']} m/s")
            c4.metric("📝 Condição",      clima["descricao"])

    with tab_r:
        st.subheader("Análise Estatística — farmtech_statistics.R")
        st.code("""# farmtech_statistics.R (original)
areas   <- c(100, 200, 300, 400, 500)
insumos <- c(50, 75, 120, 90, 60)
cat("Média das áreas:",   mean(areas),   "m²\\n")
cat("DP das áreas:",       sd(areas),     "m²\\n")
cat("Média dos insumos:", mean(insumos), "unidades\\n")
cat("DP dos insumos:",     sd(insumos),   "unidades\\n")""", language="r")
        st.markdown("**Executar no terminal:** `Rscript fase1/farmtech_statistics.R`")

        # Reprodução em Python para visualização inline
        areas_r   = [100, 200, 300, 400, 500]
        insumos_r = [50, 75, 120, 90, 60]
        df_r = pd.DataFrame({"Área (m²)": areas_r, "Insumo": insumos_r})
        col1, col2 = st.columns(2)
        col1.metric("Média das áreas",    f"{np.mean(areas_r):.1f} m²")
        col1.metric("DP das áreas",       f"{np.std(areas_r, ddof=1):.2f} m²")
        col2.metric("Média dos insumos",  f"{np.mean(insumos_r):.1f}")
        col2.metric("DP dos insumos",     f"{np.std(insumos_r, ddof=1):.2f}")
        fig_r = px.bar(df_r, x="Área (m²)", y="Insumo", title="Área × Insumo",
                       color_discrete_sequence=["#52b788"])
        st.plotly_chart(fig_r, width="stretch")


# ════════════════════════════════════════════════════════════════════════════════
# FASE 2 – BANCO DE DADOS
# ════════════════════════════════════════════════════════════════════════════════
elif pagina == "🗄️ Fase 2 – Banco de Dados":
    st.markdown('<p class="main-header">🗄️ Fase 2 — Banco de Dados (Oracle / SQLite)</p>', unsafe_allow_html=True)

    st.info("O banco Oracle original está em: [github.com/macedorafa1024/Atividades-TIA](https://github.com/macedorafa1024/Atividades-TIA)  \n"
            "Nesta consolidação, o dashboard também mantém um SQLite local com MER/DER equivalente para demonstração integrada.")

    df = carregar_dados()
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Dados dos Sensores", "🧩 SQLite Integrado", "🔎 Consultas SQL", "📊 Estatísticas"])

    with tab1:
        st.subheader("dados_agricolas.csv (300 registros)")
        st.dataframe(df.head(20), width="stretch")
        st.caption(f"Total: {len(df)} registros | Colunas: {', '.join(df.columns)}")

    with tab2:
        st.subheader("Banco relacional local da Fase 2")
        st.caption(f"Arquivo SQLite: {os.path.relpath(DB_PATH, os.path.dirname(__file__))}")
        if st.button("📥 Importar CSV para SQLite", type="primary"):
            total = importar_leituras_csv(CSV_PATH, limite=300, limpar=True)
            st.success(f"{total} leituras importadas para o banco relacional.")

        stats_db = estatisticas_banco()
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Talhões", len(listar_talhoes()))
        c2.metric("Leituras no SQLite", int(stats_db["total_leituras"] or 0))
        c3.metric("Irrigações registradas", int(stats_db["total_irrigacoes"] or 0))
        c4.metric("Alertas no banco", int(stats_db["total_alertas"] or 0))

        st.markdown("**Talhões**")
        st.dataframe(pd.DataFrame(listar_talhoes()), width="stretch")
        st.markdown("**Últimas leituras**")
        st.dataframe(pd.DataFrame(listar_leituras(limite=20)), width="stretch")
        st.markdown("**Últimas irrigações**")
        st.dataframe(pd.DataFrame(listar_irrigacoes(limite=20)), width="stretch")
        st.markdown("**Últimos alertas**")
        st.dataframe(pd.DataFrame(listar_alertas(limite=20)), width="stretch")

    with tab3:
        st.subheader("Consultas equivalentes às do Oracle (Fase 3)")
        consultas = {
            "COUNT total de registros":   f"SELECT COUNT(*) → {len(df)}",
            "Média de umidade":           f"SELECT AVG(umidade) → {df['umidade'].mean():.2f}%",
            "Média N, P, K, pH":          f"N={df['nitrogenio'].mean():.2f} | P={df['fosforo'].mean():.2f} | K={df['potassio'].mean():.2f} | pH={df['ph'].mean():.2f}",
            "Temp mínima / máxima":       f"MIN={df['temperatura'].min():.1f}°C | MAX={df['temperatura'].max():.1f}°C",
            "Irrigação LIGADA / DESLIGADA": f"LIGADA={len(df[df.status_irrigacao=='LIGADA'])} | DESLIGADA={len(df[df.status_irrigacao=='DESLIGADA'])}",
            "Volume total (L)":           f"SUM(volume_irrigacao_L) → {df['volume_irrigacao_L'].sum():,.0f} L",
        }
        for sql, res in consultas.items():
            st.code(f"{sql}\n→ {res}")

    with tab4:
        st.write(df.describe().T.style.format("{:.2f}"))


# ════════════════════════════════════════════════════════════════════════════════
# FASE 3 – SENSORES IoT
# ════════════════════════════════════════════════════════════════════════════════
elif pagina == "📡 Fase 3 – Sensores IoT":
    st.markdown('<p class="main-header">📡 Fase 3 — Sensores IoT (ESP32)</p>', unsafe_allow_html=True)
    st.info("Simula leituras do ESP32 (DHT22 + LDR) com as mesmas colunas do gerar_sensores_fase2.py original.")

    n = st.slider("Número de leituras", 1, 20, 5)
    if st.button("▶️ Simular Leituras", type="primary"):
        leituras = [verificar_irrigacao(simular_leitura()) for _ in range(n)]
        df_s = pd.DataFrame(leituras)

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Umidade média",     f"{df_s['umidade'].mean():.1f}%")
        c2.metric("pH médio",          f"{df_s['ph'].mean():.2f}")
        c3.metric("Temperatura média", f"{df_s['temperatura'].mean():.1f}°C")
        c4.metric("Irrigações LIGADAS", int(df_s['irrigar'].sum()))

        fig = px.bar(df_s.reset_index(), x="index", y="umidade",
                     color="irrigar", title="Umidade por Leitura",
                     color_discrete_map={True: "#e63946", False: "#52b788"})
        fig.add_hline(y=40, line_dash="dash", line_color="orange", annotation_text="Limite mínimo (40%)")
        st.plotly_chart(fig, width="stretch")

        st.dataframe(df_s[["umidade","temperatura","ph","nitrogenio","fosforo",
                             "potassio","chuva","volume_irrigacao_L","status_irrigacao",
                             "umidade_futura","rendimento_t_ha"]], width="stretch")

        # Alertas SNS
        for row in leituras:
            alertas = avaliar_e_alertar(row)
            for a in alertas:
                st.warning(f"🔔 **SNS** [{a['resultado_sns']['modo']}]: {a['mensagem']}")

    st.divider()
    if st.button("🔄 Regenerar dados_agricolas.csv (300 registros)", type="secondary"):
        salvar_csv(300, forcar=True)
        st.cache_data.clear()
        st.success("CSV regenerado! Recarregue a página para atualizar os dados.")


# ════════════════════════════════════════════════════════════════════════════════
# FASE 4 – MACHINE LEARNING (dashboard original integrado)
# ════════════════════════════════════════════════════════════════════════════════
elif pagina == "🤖 Fase 4 – Machine Learning":
    st.markdown('<p class="main-header">🤖 Fase 4 — Machine Learning (Assistente Agrícola)</p>', unsafe_allow_html=True)

    df = carregar_dados()
    scaler_u, modelo_u = _modelo_umidade()
    scaler_r, modelo_r = _modelo_rendimento()

    aba_dados, aba_modelo, aba_umidade, aba_rendimento = st.tabs([
        "📊 Dados & Correlações",
        "🤖 Modelo & Métricas",
        "📈 Previsão de Umidade Futura",
        "🌾 Rendimento & Manejo Agrícola",
    ])

    # ── aba_dados ───────────────────────────────────────────────────────────────
    with aba_dados:
        st.subheader("Dados coletados pelos sensores")
        st.dataframe(df.head())
        st.subheader("Estatísticas descritivas")
        st.write(df.describe())
        st.subheader("Matriz de correlação")
        corr = df.select_dtypes(include=[float, int]).corr()
        fig, ax = plt.subplots(figsize=(10, 6))
        im = ax.imshow(corr.values, interpolation="nearest", cmap="viridis")
        ax.set_xticks(range(len(corr.columns)))
        ax.set_yticks(range(len(corr.columns)))
        ax.set_xticklabels(corr.columns, rotation=45, ha="right")
        ax.set_yticklabels(corr.columns)
        for i in range(len(corr.columns)):
            for j in range(len(corr.columns)):
                ax.text(j, i, f"{corr.values[i,j]:.2f}", ha="center", va="center", fontsize=7)
        fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
        st.pyplot(fig)

    # ── aba_modelo ──────────────────────────────────────────────────────────────
    with aba_modelo:
        st.subheader("Desempenho dos modelos de regressão")
        mae_u, mse_u, rmse_u, r2_u = calcular_metricas(df, FEATURES, "umidade_futura",   scaler_u, modelo_u)
        mae_r, mse_r, rmse_r, r2_r = calcular_metricas(df, FEATURES, "rendimento_t_ha",  scaler_r, modelo_r)

        st.markdown("### Modelo de Umidade Futura")
        c1,c2,c3,c4 = st.columns(4)
        c1.metric("MAE",  f"{mae_u:.2f}")
        c2.metric("MSE",  f"{mse_u:.2f}")
        c3.metric("RMSE", f"{rmse_u:.2f}")
        c4.metric("R²",   f"{r2_u:.2f}")

        st.markdown("### Modelo de Rendimento")
        c5,c6,c7,c8 = st.columns(4)
        c5.metric("MAE",  f"{mae_r:.2f}")
        c6.metric("MSE",  f"{mse_r:.2f}")
        c7.metric("RMSE", f"{rmse_r:.2f}")
        c8.metric("R²",   f"{r2_r:.2f}")

        st.markdown("""
### 📘 Como interpretar as métricas
- **MAE**: erro médio absoluto. **Quanto menor, melhor**.
- **MSE**: erro médio ao quadrado. Penaliza erros grandes. **Quanto menor, melhor**.
- **RMSE**: raiz do MSE, na escala original da variável. **Quanto menor, melhor**.
- **R²**: capacidade explicativa do modelo. **Quanto mais próximo de 1, melhor**.
        """)

        if st.button("🔄 Re-treinar modelos", type="secondary"):
            with st.spinner("Treinando..."):
                res = treinar_modelos(forcar=True)
            st.cache_resource.clear()
            st.success(f"Modelos retreinados: {res}")

    # ── aba_umidade ─────────────────────────────────────────────────────────────
    with aba_umidade:
        st.subheader("Previsão de Umidade Futura")
        col1, col2, col3 = st.columns(3)
        with col1:
            umidade     = st.slider("Umidade atual (%)", float(df["umidade"].min()), float(df["umidade"].max()), float(df["umidade"].median()), key="u_u")
            temperatura = st.slider("Temperatura (°C)",  float(df["temperatura"].min()), float(df["temperatura"].max()), float(df["temperatura"].median()), key="t_u")
        with col2:
            ph          = st.slider("pH", float(df["ph"].min()), float(df["ph"].max()), float(df["ph"].median()), key="p_u")
            nitrogenio  = st.slider("Nitrogênio", float(df["nitrogenio"].min()), float(df["nitrogenio"].max()), float(df["nitrogenio"].median()), key="n_u")
            fosforo     = st.slider("Fósforo", float(df["fosforo"].min()), float(df["fosforo"].max()), float(df["fosforo"].median()), key="f_u")
        with col3:
            potassio    = st.slider("Potássio", float(df["potassio"].min()), float(df["potassio"].max()), float(df["potassio"].median()), key="k_u")
            chuva       = st.slider("Chuva (mm)", float(df["chuva"].min()), float(df["chuva"].max()), float(df["chuva"].median()), key="c_u")
            vol_irrig   = st.slider("Volume irrigação (L)", float(df["volume_irrigacao_L"].min()), float(df["volume_irrigacao_L"].max()), float(df["volume_irrigacao_L"].median()), key="v_u")
        status_u = st.radio("Status da Irrigação", ["DESLIGADA", "LIGADA"], key="s_u")

        if st.button("Prever umidade futura", key="btn_u"):
            entrada = pd.DataFrame([[umidade, temperatura, ph, nitrogenio, fosforo, potassio, chuva, vol_irrig, status_to_bin(status_u)]], columns=FEATURES)
            umidade_prev = modelo_u.predict(scaler_u.transform(entrada))[0]
            st.success(f"Umidade futura prevista: **{umidade_prev:.2f}%**")
            st.markdown("---")
            st.subheader("Recomendação de Irrigação")
            if umidade_prev < 30:
                st.error("⚠️ Umidade baixa: recomenda-se aumentar ou antecipar a irrigação.")
                publicar_alerta_sns("UMIDADE FUTURA CRÍTICA", f"Umidade futura prevista: {umidade_prev:.2f}%")
            elif umidade_prev > 70:
                st.warning("🔶 Umidade alta: recomenda-se reduzir irrigação para evitar encharcamento.")
            else:
                st.success("🟢 Umidade equilibrada: manter o manejo atual.")

    # ── aba_rendimento ──────────────────────────────────────────────────────────
    with aba_rendimento:
        st.subheader("Previsão de Rendimento e Manejo Agrícola")
        st.markdown("Estima o **rendimento esperado em t/ha** com base nos sensores e condições de irrigação.")
        col1, col2, col3 = st.columns(3)
        with col1:
            umidade_r    = st.slider("Umidade (%)", float(df["umidade"].min()), float(df["umidade"].max()), float(df["umidade"].median()), key="u_r")
            temperatura_r= st.slider("Temperatura (°C)", float(df["temperatura"].min()), float(df["temperatura"].max()), float(df["temperatura"].median()), key="t_r")
        with col2:
            ph_r         = st.slider("pH", float(df["ph"].min()), float(df["ph"].max()), float(df["ph"].median()), key="p_r")
            nitrogenio_r = st.slider("Nitrogênio", float(df["nitrogenio"].min()), float(df["nitrogenio"].max()), float(df["nitrogenio"].median()), key="n_r")
            fosforo_r    = st.slider("Fósforo", float(df["fosforo"].min()), float(df["fosforo"].max()), float(df["fosforo"].median()), key="f_r")
        with col3:
            potassio_r   = st.slider("Potássio", float(df["potassio"].min()), float(df["potassio"].max()), float(df["potassio"].median()), key="k_r")
            chuva_r      = st.slider("Chuva (mm)", float(df["chuva"].min()), float(df["chuva"].max()), float(df["chuva"].median()), key="c_r")
            vol_irrig_r  = st.slider("Volume irrigação (L)", float(df["volume_irrigacao_L"].min()), float(df["volume_irrigacao_L"].max()), float(df["volume_irrigacao_L"].median()), key="v_r")
        status_r = st.radio("Status da Irrigação", ["DESLIGADA", "LIGADA"], key="s_r")

        if st.button("Prever rendimento", key="btn_r"):
            entrada_r = pd.DataFrame([[umidade_r, temperatura_r, ph_r, nitrogenio_r, fosforo_r, potassio_r, chuva_r, vol_irrig_r, status_to_bin(status_r)]], columns=FEATURES)
            rendimento_prev = modelo_r.predict(scaler_r.transform(entrada_r))[0]
            st.success(f"Rendimento previsto: **{rendimento_prev:.2f} t/ha**")
            st.markdown("---")
            st.subheader("Recomendações de Manejo")
            limite_baixo = df["rendimento_t_ha"].quantile(0.33)
            limite_medio = df["rendimento_t_ha"].quantile(0.66)
            if rendimento_prev < limite_baixo:
                st.error("⚠️ Baixo rendimento esperado.")
                st.write("- Reforçar fertilização (Nitrogênio).\n- Revisar volume/frequência de irrigação.\n- Verificar pH do solo.")
            elif rendimento_prev < limite_medio:
                st.warning("🔶 Rendimento médio esperado.")
                st.write("- Monitorar equilíbrio NPK.\n- Ajustar irrigação conforme clima.\n- Acompanhar sensores diariamente.")
            else:
                st.success("🟢 Alto rendimento esperado.")
                st.write("- Manter manejo atual.\n- Evitar excesso de irrigação.\n- Continuar monitorando sensores.")
            st.info("Recomendações baseadas no modelo de IA. A decisão final deve considerar orientação agronômica.")


# ════════════════════════════════════════════════════════════════════════════════
# FASE 5 – ALERTAS AWS SNS
# ════════════════════════════════════════════════════════════════════════════════
elif pagina == "☁️ Fase 5 – Alertas AWS":
    st.markdown('<p class="main-header">☁️ Fase 5 — Alertas via Amazon SNS</p>', unsafe_allow_html=True)

    st.info("Configure `SNS_TOPIC_ARN` ou `AWS_SNS_TOPIC_ARN` e `AWS_REGION` no `.env` para envio real de e-mail.  \n"
            "Sem configuração, os alertas são salvos em `data/alertas_sns.log`.")

    st.subheader("Disparar Alerta Manual")
    c1, c2, c3 = st.columns(3)
    um_t  = c1.number_input("Umidade (%)",       10.0, 100.0, 35.0)
    ph_t  = c2.number_input("pH",                4.5,  8.5,   5.0)
    tmp_t = c3.number_input("Temperatura (°C)", 15.0,  45.0,  39.0)

    if st.button("📤 Avaliar e Disparar Alertas SNS", type="primary"):
        alertas = avaliar_e_alertar({"umidade_pct": um_t, "ph": ph_t, "temperatura_c": tmp_t})
        if alertas:
            for a in alertas:
                st.warning(f"🔔 **{a['tipo'].upper()}** | Modo `{a['resultado_sns']['modo']}`: {a['mensagem']}")
        else:
            st.success("✅ Leitura dentro dos parâmetros. Nenhum alerta gerado.")

    st.divider()
    log_path = os.path.join("data", "alertas_sns.log")
    st.subheader("📋 Histórico de Alertas")
    alertas_db = pd.DataFrame(listar_alertas(limite=30))
    if not alertas_db.empty:
        st.markdown("**Banco SQLite**")
        st.dataframe(alertas_db, width="stretch")
    else:
        st.info("Nenhum alerta registrado no banco ainda.")

    st.markdown("**Log local**")
    if os.path.exists(log_path):
        with open(log_path) as f:
            st.code("".join(f.readlines()[-20:]))
    else:
        st.info("Nenhum alerta disparado ainda.")

    st.divider()
    st.subheader("⚙️ Configuração AWS SNS (Passo a passo)")
    st.markdown("""
1. Acesse **AWS Console → SNS → Tópicos → Criar tópico** (Standard, nome: `farmtech-alertas`)
2. Copie o ARN do tópico criado
3. Crie uma **Assinatura**: protocolo `Email`, endpoint `seu@email.com`
4. Confirme o e-mail recebido na caixa de entrada
5. Configure o `.env`:
```
AWS_REGION=us-east-1
SNS_TOPIC_ARN=arn:aws:sns:us-east-1:XXXXXXXXXXXX:farmtech-alertas
# ou
AWS_SNS_TOPIC_ARN=arn:aws:sns:us-east-1:XXXXXXXXXXXX:farmtech-alertas
```
6. Instale boto3: `pip install boto3`
    """)


# ════════════════════════════════════════════════════════════════════════════════
# FASE 6 – VISÃO COMPUTACIONAL
# ════════════════════════════════════════════════════════════════════════════════
elif pagina == "👁️ Fase 6 – Visão Computacional":
    st.markdown('<p class="main-header">👁️ Fase 6 — Visão Computacional (YOLOv5)</p>', unsafe_allow_html=True)

    st.info("O modelo YOLOv5 foi treinado no Google Colab.  \n"
            "Repositório: [github.com/macedorafa1024/Cap1_Fase6](https://github.com/macedorafa1024/Cap1_Fase6)")

    from fase6.visao_computacional import processar_pasta_imagens, analisar_imagem
    if "alertas_visao_enviados" not in st.session_state:
        st.session_state["alertas_visao_enviados"] = set()

    tab_pasta, tab_upload = st.tabs(["📂 Processar Pasta", "📤 Upload de Imagem"])

    with tab_pasta:
        pasta = st.text_input("Caminho da pasta de imagens", "fase6/imagens")
        if st.button("🔍 Analisar Imagens", type="primary"):
            with st.spinner("Processando..."):
                resultados = processar_pasta_imagens(pasta)
            total     = len(resultados)
            saudaveis = sum(1 for r in resultados if r["saudavel"])
            c1, c2, c3 = st.columns(3)
            c1.metric("Imagens", total)
            c2.metric("✅ Saudáveis", saudaveis)
            c3.metric("⚠️ Com Anomalias", total - saudaveis)
            for r in resultados:
                icone = "✅" if r["saudavel"] else "⚠️"
                with st.expander(f"{icone} {r['imagem']} [{r['modo']}]"):
                    for d in r["deteccoes"]:
                        cor = "green" if d["classe"] == "soja_saudavel" else "red"
                        st.markdown(f"- :{cor}[**{d['classe']}**] — {d['confianca']:.1%}")
                    if not r["saudavel"]:
                        for d in r["pragas_encontradas"]:
                            chave_alerta = f"{r['imagem']}|{d['classe']}"
                            if chave_alerta not in st.session_state["alertas_visao_enviados"]:
                                alertar_praga(d["classe"], d["confianca"])
                                st.session_state["alertas_visao_enviados"].add(chave_alerta)

    with tab_upload:
        uploaded = st.file_uploader("Enviar imagem", type=["jpg","jpeg","png"])
        if uploaded:
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
                tmp.write(uploaded.read())
                tmp_path = tmp.name
            st.image(tmp_path, width="stretch")
            if st.button("🔍 Analisar", type="primary"):
                res = analisar_imagem(tmp_path)
                for d in res["deteccoes"]:
                    fn = st.success if d["classe"] == "soja_saudavel" else st.error
                    fn(f"{'✅' if d['classe']=='soja_saudavel' else '⚠️'} {d['classe']} — {d['confianca']:.1%}")
