import streamlit as st
import pandas as pd
from github import Github
import io
from datetime import datetime

# 1. PREVENÇÃO CONTRA TRADUTOR E IDIOMA
st.markdown('<html lang="pt-br">', unsafe_allow_html=True)

# 2. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Aura Apoena Logistics", layout="wide")

# 3. UI/UX DESIGNER - ESTILO PADRONIZADO
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    [data-testid="stSidebar"] {
        background-color: #002D5E !important;
        min-width: 280px;
    }
    .logo-shadow {
        filter: drop-shadow(0px 6px 10px rgba(0,0,0,0.6));
        text-align: center;
        padding: 10px;
    }
    .stTextInput input, .stSelectbox div[data-baseweb="select"], .stDateInput input, .stNumberInput input {
        background-color: #F0F7FF !important; 
        border: 2px solid #002D5E !important;
        color: #000000 !important;
        border-radius: 8px !important;
        height: 45px !important;
    }
    label, .stMarkdown p {
        color: #002D5E !important;
        font-weight: bold !important;
    }
    div.stButton > button {
        background-color: #E1E8F0 !important;
        color: #002D5E !important;
        border: 2px solid #002D5E !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        width: 100% !important;
        height: 50px !important;
        transition: all 0.3s !important;
    }
    div.stButton > button:hover {
        background-color: #002D5E !important;
        color: #E1E8F0 !important;
    }
    [data-testid="stDataFrame"], [data-testid="stTable"], .stDataEditor {
        background-color: #FFFFFF !important;
        border-radius: 10px !important;
    }
    h1, h2, h3 { color: #002D5E !important; font-weight: 700 !important; }
    [data-testid="stSidebar"] .stMarkdown p, [data-testid="stSidebar"] label {
        color: #FFFFFF !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 4. BACKEND (CONEXÃO GITHUB)
def carregar_sistema():
    colunas = ["Passageiro", "Motorista", "Data", "Trajeto", "Hotel (R$)", "Combustível (R$)", "Aéreo (R$)", "Outros (R$)", "Desc. Outros", "Total (R$)"]
    try:
        g = Github(st.secrets["GITHUB_TOKEN"])
        repo = g.get_repo("yaramaia122-lgtm/logistica-aura")
        contents = repo.get_contents("dados_logistica.csv")
        df = pd.read_csv(io.StringIO(contents.decoded_content.decode()))
        # Garante que todas as colunas novas existam no arquivo carregado
        for col in colunas:
            if col not in df.columns:
                df[col] = 0.0 if "R$" in col else ""
        return df, contents.sha, repo
    except:
        return pd.DataFrame(columns=colunas), None, None

df, sha, repo = carregar_sistema()

# 5. SIDEBAR / MENU
with st.sidebar:
    st.markdown("<br>", unsafe_allow_html=True)
    logo_path = "https://raw.githubusercontent.com/yaramaia122-lgtm/logistica-aura/main/Aura%20(Azul%20e%20Ocre)%20(1).png"
    st.markdown(f'<div class="logo-shadow"><img src="{logo_path}" width="220"></div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    menu = st.radio("NAVEGAÇÃO:", ["📋 Agenda de Viagens", "📝 Programar Viagem", "💰 Financeiro"])

# 6. TELAS

if menu == "📋 Agenda de Viagens":
    st.title("📋 Agenda de Viagens")
    if not df.empty:
        # Apenas colunas logísticas para a Agenda
        st.dataframe(df[["Passageiro", "Motorista", "Data", "Trajeto"]], use_container_width=True)
    else:
        st.info("Agenda vazia.")

elif menu == "📝 Programar Viagem":
    st.title("📝 Programar Viagem")
    with st.form("form_v", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            nome = st.text_input("Nome do Passageiro").upper()
            motorista = st.selectbox("Motorista", ["Ilson", "Antonio", "Outro"])
            hotel = st.number_input("Valor Hotel (R$)", min_value=0.0, step=1.0)
            aereo = st.number_input("Valor Aéreo (R$)", min_value=0.0, step=1.0)
        with c2:
            data = st.date_input("Data da Viagem", datetime.now())
            trajeto = st.selectbox("Itinerário", ["P. Lacerda x Cuiabá", "Interno", "Outro"])
            combustivel = st.number_input("Valor Combustível (R$)", min_value=0.0, step=1.0)
            outros = st.number_input("Outros Custos (R$)", min_value=0.0, step=1.0)
        
        desc_outros = st.text_input("Descrição de Outros Custos")
        
        if st.form_submit_button("SALVAR REGISTRO"):
            if nome and repo:
                total = hotel + combustivel + aereo + outros
                nova_viagem = pd.
