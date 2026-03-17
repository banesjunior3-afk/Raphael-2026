import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import os

st.set_page_config(page_title="Dashboard | Dr. Raphael Mota 2026", page_icon="🗳️", layout="wide")

CSS = """
<style>
.stApp { background-color: #001a3e; color: white; }
header[data-testid="stHeader"] { background: #001a3e; }
.stMetric { background-color: #002868; border-radius: 12px; padding: 16px; border: 1px solid #FFD700; }
.stMetric label { color: #FFD700 !important; font-weight: 700; }
.stMetric [data-testid="stMetricValue"] { color: white !important; font-size: 2rem !important; }
div[data-testid="stSidebar"] { background-color: #001030; }
.stButton > button { background-color: #002868; color: #FFD700; border: 2px solid #FFD700; font-weight: 700; border-radius: 8px; }
h1, h2, h3 { color: #FFD700 !important; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

SENHA = os.environ.get("DASHBOARD_SENHA", "raphael2026")

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        LOGIN_HTML = """
        <div style='text-align:center;padding:40px 0 20px 0;'>
            <h1 style='color:#FFD700;font-size:2.5rem;'>🦷 DR. RAPHAEL MOTA</h1>
            <p style='color:white;font-size:1.2rem;letter-spacing:3px;'>DEPUTADO FEDERAL 2026</p>
            <hr style='border-color:#FFD700;margin:20px 0;'>
        </div>
        """
        st.markdown(LOGIN_HTML, unsafe_allow_html=True)
        senha = st.text_input("Senha de acesso", type="password", placeholder="••••••••")
        if st.button("Entrar", use_container_width=True):
            if senha == SENHA:
                st.session_state.autenticado = True
                st.rerun()
            else:
                st.error("Senha incorreta.")
    st.stop()

META_VOTOS        = 42000
META_CONSERVADORA = 35000
META_OTIMISTA     = 60000

@st.cache_data(ttl=3600)
def carregar_base():
    url = "https://raw.githubusercontent.com/banesjunior3-afk/Raphael-2026/main/base_raphael_v2.csv"
    return pd.read_csv(url)

@st.cache_data(ttl=300)
def carregar_apoiadores():
    SHEET_ID = os.environ.get("SHEET_ID", "")
    if not SHEET_ID:
        return pd.DataFrame(columns=["Municipio","Nome do Apoiador","Cargo/Categoria","Votos Prometidos","Data de Cadastro","Observacoes"])
    try:
        url = "https://docs.google.com/spreadsheets/d/" + SHEET_ID + "/export?format=csv&gid=0"
        df = pd.read_csv(url)
        df.columns = df.columns.str.strip()
        if "Votos Prometidos" in df.columns:
            df["Votos Prometidos"] = pd.to_numeric(df["Votos Prometidos"], errors="coerce").fillna(0)
            df["Votos Reais"] = (df["Votos Prometidos"] * 0.30).round(0).astype(int)
        return df
    except Exception as e:
        return pd.DataFrame(columns=["Municipio","Nome do Apoiador","Cargo/Categoria","Votos Prometidos","Data de Cadastro","Observacoes"])

@st.cache_data
def carregar_geojson():
    url = "https://raw.githubusercontent.com/tbrugz/geodata-br/master/geojson/geojs-31-mun.json"
    r = requests.get(url)
    return r.json()

base       = carregar_base()
apoiadores = carregar_apoiadores()
geojson    = carregar_geojson()

col1, col2 = st.columns([3,1])
with col1:
    HEADER_HTML = """
    <h1 style='margin-bottom:0;'>🦷 Dr. Raphael Mota</h1>
    <p style='color:white;font-size:1rem;letter-spacing:2px;margin-top:4px;'>DEPUTADO FEDERAL · PL · MINAS GERAIS · 2026</p>
    """
    st.markdown(HEADER_HTML, unsafe_allow_html=True)
with col2:
    if st.button("🔄 Atualizar"):
        st.cache_data.clear()
        st.rerun()

st.markdown('<hr style="border-color:#FFD700;margin:10px 0 20px 0;">', unsafe_allow_html=True)

votos_prometidos = int(apoiadores["Votos Prometidos"].sum()) if "Votos Prometidos" in apoiadores.columns else 0
votos_reais      = int(votos_prometidos * 0.30)
num_apoiadores   = len(apoiadores)
num_municipios   = apoiadores["Municipio"].nunique() if "Municipio" in apoiadores.columns else 0
pct_meta         = round(votos_reais / META_VOTOS * 100, 1)

c1,c2,c3,c4,c5 = st.columns(5)
c1.metric("🗳️ Prometidos",  str(votos_prometidos))
c2.metric("✅ Reais Est.",   str(votos_reais), str(pct_meta) + "% da meta")
c3.metric("🎯 Meta",         str(META_VOTOS))
c4.metric("👥 Apoiadores",   str(num_apoiadores))
c5.metric("📍 Municípios",   str(num_municipios))

st.markdown("---")
st.subheader("🌡️ Termômetro de Votos")

fig_termo = go.Figure(go.Bar(
    x=[votos_reais], y=[""],
    orientation="h",
    marker_color="#FFD700",
    text=[str(votos_reais) + " votos (" + str(pct_meta) + "%)"],
    textposition="inside",
    textfont=dict(color="#002868", size=14)
))
fig_termo.add_vline(x=META_CONSERVADORA, line_dash="dash", line_color="orange",
    annotation_text="Minimo " + str(META_CONSERVADORA))
fig_termo.add_vline(x=META_VOTOS, line_dash="dash", line_color="lime",
    annotation_text="Meta " + str(META_VOTOS))
fig_termo.add_vline(x=META_OTIMISTA, line_dash="dash", line_color="cyan",
    annotation_text="Otimista " + str(META_OTIMISTA))
fig_termo.update_layout(
    xaxis=dict(range=[0, META_OTIMISTA*1.1], color="white"),
    paper_bgcolor="#001a3e", plot_bgcolor="#002868",
    height=120, margin=dict(l=10,r=10,t=20,b=10)
)
st.plotly_chart(fig_termo, use_container_width=True)

st.markdown("---")
st.subheader("🗺️ Mapa de Minas Gerais")

base_mapa = base.copy()
base_mapa["CIDADE_NORM"] = base_mapa["CIDADE"].str.upper().str.strip()

if "Municipio" in apoiadores.columns and len(apoiadores) > 0:
    agg = apoiadores.groupby("Municipio").agg(
        VOTOS_PROMETIDOS=("Votos Prometidos","sum"),
        NUM_APOIADORES=("Nome do Apoiador","count")
    ).reset_index()
    agg["CIDADE_NORM"] = agg["Municipio"].str.upper().str.strip()
    base_mapa = base_mapa.merge(
        agg[["CIDADE_NORM","VOTOS_PROMETIDOS","NUM_APOIADORES"]],
        on="CIDADE_NORM", how="left"
    )
else:
    base_mapa["VOTOS_PROMETIDOS"] = 0
    base_mapa["NUM_APOIADORES"]   = 0

base_mapa["VOTOS_PROMETIDOS"] = base_mapa["VOTOS_PROMETIDOS"].fillna(0)
base_mapa["NUM_APOIADORES"]   = base_mapa["NUM_APOIADORES"].fillna(0)

mun_geo = {}
for f in geojson["features"]:
    nome = f["properties"]["name"].upper()
    cod  = f["properties"]["id"]
    mun_geo[nome] = cod

base_mapa["COD_IBGE"] = base_mapa["CIDADE_NORM"].map(mun_geo)

tier_cores = {"A":"#FFD700","B":"#4A90D9","C":"#2E5B8F","D":"#1a3050"}

fig_mapa = px.choropleth(
    base_mapa,
    geojson=geojson,
    locations="COD_IBGE",
    featureidkey="properties.id",
    color="TIER",
    color_discrete_map=tier_cores,
    hover_name="CIDADE",
    hover_data={
        "TIER": True,
        "SCORE_FINAL": True,
        "QTD": True,
        "QT_VOTOS": True,
        "VOTOS_PROMETIDOS": True,
        "NUM_APOIADORES": True,
        "COD_IBGE": False
    },
    labels={
        "TIER": "Tier",
        "SCORE_FINAL": "Score",
        "QTD": "Dentistas",
        "QT_VOTOS": "Votos PL/Nikolas",
        "VOTOS_PROMETIDOS": "Votos Prometidos",
        "NUM_APOIADORES": "Apoiadores"
    }
)
fig_mapa.update_geos(fitbounds="locations", visible=False)
fig_mapa.update_layout(
    paper_bgcolor="#001a3e",
    plot_bgcolor="#001a3e",
    height=600,
    margin=dict(l=0,r=0,t=0,b=0),
    legend=dict(
        bgcolor="#002868",
        font=dict(color="white"),
        title=dict(text="Tier", font=dict(color="#FFD700"))
    )
)
st.plotly_chart(fig_mapa, use_container_width=True)

c1,c2,c3,c4 = st.columns(4)
c1.markdown('<div style="background:#FFD700;padding:8px;border-radius:6px;text-align:center;color:#001a3e;font-weight:700;">🏆 Tier A — Prioritário</div>', unsafe_allow_html=True)
c2.markdown('<div style="background:#4A90D9;padding:8px;border-radius:6px;text-align:center;color:white;font-weight:700;">🔷 Tier B — Alto Potencial</div>', unsafe_allow_html=True)
c3.markdown('<div style="background:#2E5B8F;padding:8px;border-radius:6px;text-align:center;color:white;font-weight:700;">⬜ Tier C — Secundário</div>', unsafe_allow_html=True)
c4.markdown('<div style="background:#1a3050;padding:8px;border-radius:6px;text-align:center;color:white;font-weight:700;">⬛ Tier D — Baixa Prioridade</div>', unsafe_allow_html=True)

st.markdown("---")
col1, col2 = st.columns(2)

with col1:
    st.subheader("🏆 Top 20 por Score")
    top20 = base_mapa.sort_values("SCORE_FINAL", ascending=False).head(20)[
        ["CIDADE","TIER","SCORE_FINAL","QTD","QT_VOTOS"]
    ].rename(columns={
        "CIDADE":"Cidade","TIER":"Tier","SCORE_FINAL":"Score",
        "QTD":"Dentistas","QT_VOTOS":"Votos PL/Nikolas"
    })
    st.dataframe(top20, use_container_width=True, hide_index=True)

with col2:
    st.subheader("⚠️ Tier A sem Apoiadores")
    sem_apoio = base_mapa[
        (base_mapa["TIER"]=="A") & (base_mapa["NUM_APOIADORES"]==0)
    ].sort_values("SCORE_FINAL", ascending=False).head(20)[
        ["CIDADE","SCORE_FINAL","QTD","QT_VOTOS"]
    ].rename(columns={
        "CIDADE":"Cidade","SCORE_FINAL":"Score",
        "QTD":"Dentistas","QT_VOTOS":"Votos PL/Nikolas"
    })
    if len(sem_apoio) > 0:
        st.dataframe(sem_apoio, use_container_width=True, hide_index=True)
    else:
        st.success("✅ Todos os municípios Tier A têm apoiadores!")

st.markdown("---")
st.subheader("👥 Apoiadores Cadastrados")

SHEET_ID = os.environ.get("SHEET_ID","")
st.markdown("[📋 Abrir planilha de apoiadores](https://docs.google.com/spreadsheets/d/" + SHEET_ID + ")")

if len(apoiadores) > 0:
    filtro = st.selectbox("Filtrar por Tier", ["Todos","A","B","C","D"])
    apo = apoiadores.copy()
    if "Municipio" in apo.columns:
        apo["CIDADE_NORM"] = apo["Municipio"].str.upper().str.strip()
        apo = apo.merge(
            base_mapa[["CIDADE_NORM","TIER","SCORE_FINAL"]],
            on="CIDADE_NORM", how="left"
        )
    if filtro != "Todos":
        apo = apo[apo["TIER"]==filtro]
    cols_show = [c for c in ["Municipio","Nome do Apoiador","Cargo/Categoria",
                              "Votos Prometidos","Votos Reais","TIER","SCORE_FINAL","Observacoes"]
                 if c in apo.columns]
    st.dataframe(apo[cols_show], use_container_width=True, hide_index=True)
else:
    st.info("Nenhum apoiador cadastrado ainda. Acesse a planilha para adicionar.")

st.markdown('<hr style="border-color:#FFD700;margin:30px 0 10px 0;"><p style="text-align:center;color:gray;font-size:0.8rem;">Dashboard desenvolvido por Banes Júnior · Dados TSE + CFO/CRO-MG · 2026</p>', unsafe_allow_html=True)
