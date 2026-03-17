import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import os

st.set_page_config(page_title="Dashboard | Dr. Raphael Mota 2026", page_icon="🗳️", layout="wide")

CSS = """
<style>
/* Fundo geral */
.stApp { background-color: #F8F9FA; color: #1a1a2e; }
header[data-testid="stHeader"] { background: #F8F9FA; }

/* Métricas */
div[data-testid="stMetric"] {
    background-color: white;
    border-radius: 12px;
    padding: 16px;
    border: 1px solid #e0e0e0;
    border-left: 4px solid #002868;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}
div[data-testid="stMetric"] label { color: #002868 !important; font-weight: 700; font-size: 0.85rem; }
div[data-testid="stMetric"] [data-testid="stMetricValue"] { color: #1a1a2e !important; font-size: 1.8rem !important; font-weight: 800; }
div[data-testid="stMetric"] [data-testid="stMetricDelta"] { color: #28a745 !important; font-weight: 600; }

/* Botões */
.stButton > button {
    background-color: #002868;
    color: #FFD700;
    border: none;
    font-weight: 700;
    border-radius: 8px;
    padding: 8px 20px;
}
.stButton > button:hover { background-color: #FFD700; color: #002868; }

/* Títulos */
h1 { color: #002868 !important; }
h2, h3 { color: #002868 !important; border-bottom: 2px solid #FFD700; padding-bottom: 6px; }

/* Tabelas */
div[data-testid="stDataFrame"] { border-radius: 12px; overflow: hidden; border: 1px solid #e0e0e0; }

/* Selectbox */
div[data-baseweb="select"] { border-radius: 8px !important; }

/* Sidebar */
div[data-testid="stSidebar"] { background-color: #002868; }

/* Cards de explicação */
.card-info {
    background: white;
    border-radius: 10px;
    padding: 12px 16px;
    margin: 8px 0 20px 0;
    border-left: 4px solid #FFD700;
    color: #555;
    font-size: 0.9rem;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}

/* Mobile */
@media (max-width: 768px) {
    div[data-testid="stMetric"] [data-testid="stMetricValue"] { font-size: 1.4rem !important; }
    h1 { font-size: 1.6rem !important; }
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

SENHA = os.environ.get("DASHBOARD_SENHA", "raphael2026")

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("""
        <div style='text-align:center;padding:60px 0 30px 0;'>
            <div style='font-size:3rem;'>🦷</div>
            <h1 style='color:#002868;font-size:2rem;margin:8px 0 4px 0;'>Dr. Raphael Mota</h1>
            <p style='color:#666;font-size:1rem;letter-spacing:3px;margin:0;'>DEPUTADO FEDERAL · 2026</p>
            <hr style='border:none;border-top:2px solid #FFD700;margin:20px 0;'>
            <p style='color:#888;font-size:0.85rem;'>Acesso restrito à equipe de campanha</p>
        </div>
        """, unsafe_allow_html=True)
        senha = st.text_input("", type="password", placeholder="Digite sua senha de acesso")
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
VOTOS_CRO         = 12502
PCT_CRO           = 60.99

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

# ── HEADER ────────────────────────────────────────────────
col1, col2 = st.columns([4,1])
with col1:
    st.markdown("""
    <div style='padding:10px 0 4px 0;'>
        <h1 style='margin:0;font-size:1.8rem;'>🦷 Dr. Raphael Mota</h1>
        <p style='color:#666;font-size:0.9rem;letter-spacing:2px;margin:2px 0 0 0;'>DEPUTADO FEDERAL · PL · MINAS GERAIS · 2026</p>
    </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔄 Atualizar"):
        st.cache_data.clear()
        st.rerun()

st.markdown('<hr style="border:none;border-top:2px solid #FFD700;margin:8px 0 20px 0;">', unsafe_allow_html=True)

# ── MÉTRICAS ──────────────────────────────────────────────
votos_prometidos = int(apoiadores["Votos Prometidos"].sum()) if "Votos Prometidos" in apoiadores.columns else 0
votos_reais      = int(votos_prometidos * 0.30)
num_apoiadores   = len(apoiadores)
num_municipios   = apoiadores["Municipio"].nunique() if "Municipio" in apoiadores.columns else 0
pct_meta         = round(votos_reais / META_VOTOS * 100, 1)

c1,c2,c3,c4,c5,c6 = st.columns(6)
c1.metric("🗳️ Prometidos",    f"{votos_prometidos:,}")
c2.metric("✅ Reais Est.",     f"{votos_reais:,}",    f"{pct_meta}% da meta")
c3.metric("🎯 Meta Realista", f"{META_VOTOS:,}")
c4.metric("🦷 Base CRO",      f"{VOTOS_CRO:,}",      f"{PCT_CRO}% no 2º turno")
c5.metric("👥 Apoiadores",    f"{num_apoiadores:,}")
c6.metric("📍 Municípios",    f"{num_municipios:,}")

st.markdown("""
<div class='card-info'>
💡 <b>Como ler:</b> <b>Prometidos</b> = total declarado pelos apoiadores. <b>Reais Est.</b> = projeção conservadora (30% dos prometidos — padrão eleitoral). 
<b>Base CRO</b> = votos reais na eleição do conselho em dez/2025 — sua âncora de credibilidade. <b>Meta</b> = 42.000 votos garante eleição com margem segura.
</div>
""", unsafe_allow_html=True)

# ── TERMÔMETRO ────────────────────────────────────────────
st.markdown("---")
st.subheader("🌡️ Termômetro de Votos")

fig_termo = go.Figure(go.Bar(
    x=[max(votos_reais, 500)], y=[""],
    orientation="h",
    marker_color="#002868",
    text=[f"{votos_reais:,} votos ({pct_meta}%)"],
    textposition="inside",
    textfont=dict(color="white", size=13)
))
fig_termo.add_vline(x=META_CONSERVADORA, line_dash="dash", line_color="#FF8C00",
    annotation_text=f"Mínimo {META_CONSERVADORA:,}", annotation_font_color="#FF8C00")
fig_termo.add_vline(x=META_VOTOS, line_dash="dash", line_color="#28a745",
    annotation_text=f"Meta {META_VOTOS:,}", annotation_font_color="#28a745")
fig_termo.add_vline(x=META_OTIMISTA, line_dash="dash", line_color="#007bff",
    annotation_text=f"Otimista {META_OTIMISTA:,}", annotation_font_color="#007bff")
fig_termo.update_layout(
    xaxis=dict(range=[0, META_OTIMISTA*1.1], color="#333",
               tickformat=",", gridcolor="#eee"),
    paper_bgcolor="white", plot_bgcolor="#f8f9fa",
    height=130, margin=dict(l=10,r=10,t=30,b=10)
)
st.plotly_chart(fig_termo, use_container_width=True)
st.markdown("""
<div class='card-info'>
📊 <b>Como ler o termômetro:</b> A barra azul mostra seus votos reais estimados. 
<b>Mínimo (35k)</b> = piso histórico do PL/MG. <b>Meta (42k)</b> = posição confortável na bancada. <b>Otimista (60k)</b> = top 5 do PL.
</div>
""", unsafe_allow_html=True)

# ── MAPA ─────────────────────────────────────────────────
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
    base_mapa = base_mapa.merge(agg[["CIDADE_NORM","VOTOS_PROMETIDOS","NUM_APOIADORES"]], on="CIDADE_NORM", how="left")
else:
    base_mapa["VOTOS_PROMETIDOS"] = 0
    base_mapa["NUM_APOIADORES"]   = 0

base_mapa["VOTOS_PROMETIDOS"] = base_mapa["VOTOS_PROMETIDOS"].fillna(0)
base_mapa["NUM_APOIADORES"]   = base_mapa["NUM_APOIADORES"].fillna(0)

mun_geo = {f["properties"]["name"].upper(): f["properties"]["id"] for f in geojson["features"]}
base_mapa["COD_IBGE"] = base_mapa["CIDADE_NORM"].map(mun_geo)

tier_cores = {"A":"#FFD700","B":"#4A90D9","C":"#93b8d8","D":"#d0dce8"}

fig_mapa = px.choropleth(
    base_mapa, geojson=geojson,
    locations="COD_IBGE", featureidkey="properties.id",
    color="TIER", color_discrete_map=tier_cores,
    hover_name="CIDADE",
    hover_data={
        "TIER":True,"SCORE_FINAL":True,"QTD":True,
        "QT_VOTOS":True,"VOTOS_PROMETIDOS":True,
        "NUM_APOIADORES":True,"COD_IBGE":False
    },
    labels={
        "TIER":"Tier","SCORE_FINAL":"Score","QTD":"Dentistas",
        "QT_VOTOS":"Votos PL/Nikolas","VOTOS_PROMETIDOS":"Votos Prometidos",
        "NUM_APOIADORES":"Apoiadores"
    }
)
fig_mapa.update_geos(fitbounds="locations", visible=False, bgcolor="rgba(0,0,0,0)")
fig_mapa.update_layout(
    paper_bgcolor="white", plot_bgcolor="white",
    height=580, margin=dict(l=0,r=0,t=0,b=0),
    legend=dict(bgcolor="white", font=dict(color="#1a1a2e"),
                title=dict(text="Tier", font=dict(color="#002868")))
)
st.plotly_chart(fig_mapa, use_container_width=True)

c1,c2,c3,c4 = st.columns(4)
c1.markdown('<div style="background:#FFD700;padding:10px;border-radius:8px;text-align:center;color:#002868;font-weight:700;">🏆 Tier A — Prioritário</div>', unsafe_allow_html=True)
c2.markdown('<div style="background:#4A90D9;padding:10px;border-radius:8px;text-align:center;color:white;font-weight:700;">🔷 Tier B — Alto Potencial</div>', unsafe_allow_html=True)
c3.markdown('<div style="background:#93b8d8;padding:10px;border-radius:8px;text-align:center;color:white;font-weight:700;">⬜ Tier C — Secundário</div>', unsafe_allow_html=True)
c4.markdown('<div style="background:#d0dce8;padding:10px;border-radius:8px;text-align:center;color:#333;font-weight:700;">⬛ Tier D — Baixa Prioridade</div>', unsafe_allow_html=True)

st.markdown("""
<div class='card-info'>
🗺️ <b>Como ler o mapa:</b> Cada município é colorido pelo seu <b>Tier estratégico</b> — combinação de densidade de dentistas + força do voto PL/Nikolas + custo-benefício territorial.
<b>Amarelo (Tier A)</b> = onde cada real investido tem maior retorno. Passe o mouse sobre qualquer município para ver os detalhes.
</div>
""", unsafe_allow_html=True)

# ── RANKINGS ─────────────────────────────────────────────
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
    st.markdown("""
    <div class='card-info'>
    📋 Municípios com melhor combinação de dentistas + força PL + custo de campanha. 
    Priorize esses territórios para eventos, visitas e tráfego pago.
    </div>
    """, unsafe_allow_html=True)

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
        st.markdown("""
        <div class='card-info'>
        🎯 Esses são municípios Tier A onde você ainda não tem nenhum apoiador cadastrado.
        São oportunidades de alto retorno esperando ativação — cada contato aqui vale mais.
        </div>
        """, unsafe_allow_html=True)
    else:
        st.success("✅ Todos os municípios Tier A têm apoiadores!")

# ── APOIADORES ────────────────────────────────────────────
st.markdown("---")
st.subheader("👥 Apoiadores Cadastrados")

SHEET_ID = os.environ.get("SHEET_ID","")
PDF_URL  = "https://raw.githubusercontent.com/banesjunior3-afk/Raphael-2026/main/analise_raphael_2026.pdf"

col1, col2 = st.columns(2)
with col1:
    st.markdown(f"📋 [Abrir planilha de apoiadores](https://docs.google.com/spreadsheets/d/{SHEET_ID}) — adicione novos apoiadores aqui")
with col2:
    st.markdown(f"📄 [Baixar análise estratégica completa (PDF)]({PDF_URL}) — documento Íris · Banes Júnior · Mar/2026")

st.markdown("""
<div class='card-info'>
👥 <b>Como usar a planilha:</b> Preencha o nome do município exatamente como aparece no mapa,
o nome do apoiador, cargo/categoria (ex: Dentista, Médico, Liderança política), quantidade de votos prometidos e observações.
Os votos reais estimados (30%) são calculados automaticamente. Clique em 🔄 Atualizar para ver os novos dados.
</div>
""", unsafe_allow_html=True)

if len(apoiadores) > 0:
    filtro = st.selectbox("Filtrar por Tier", ["Todos","A","B","C","D"])
    apo = apoiadores.copy()
    if "Municipio" in apo.columns:
        apo["CIDADE_NORM"] = apo["Municipio"].str.upper().str.strip()
        apo = apo.merge(base_mapa[["CIDADE_NORM","TIER","SCORE_FINAL"]], on="CIDADE_NORM", how="left")
    if filtro != "Todos":
        apo = apo[apo["TIER"]==filtro]
    cols_show = [c for c in ["Municipio","Nome do Apoiador","Cargo/Categoria",
                              "Votos Prometidos","Votos Reais","TIER","SCORE_FINAL","Observacoes"]
                 if c in apo.columns]
    st.dataframe(apo[cols_show], use_container_width=True, hide_index=True)
else:
    st.info("Nenhum apoiador cadastrado ainda. Acesse a planilha acima para começar.")

st.markdown('<hr style="border:none;border-top:1px solid #e0e0e0;margin:30px 0 10px 0;"><p style="text-align:center;color:#aaa;font-size:0.8rem;">Dashboard desenvolvido por Banes Júnior · Dados TSE + CFO/CRO-MG · 2026</p>', unsafe_allow_html=True)
