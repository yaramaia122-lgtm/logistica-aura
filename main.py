import streamlit as st
import pandas as pd
from github import Github
import io
import os
from datetime import datetime

# 1. PREVENÇÃO CONTRA TRADUTOR E IDIOMA
st.markdown('<html lang="pt-br">', unsafe_allow_html=True)

# 2. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Aura Apoena Logistics", layout="wide")

# 3. UI/UX - DESIGN PADRONIZADO
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    [data-testid="stSidebar"] { background-color: #002D5E !important; min-width: 280px; }
    .logo-container { text-align: center; padding: 20px 10px; filter: drop-shadow(0px 10px 15px rgba(0,0,0,0.8)); }
    .stTextInput input, .stSelectbox div[data-baseweb="select"], .stDateInput input, .stNumberInput input {
        background-color: #F0F7FF !important; 
        border: 2px solid #002D5E !important;
        color: #000000 !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
    }
    label, .stMarkdown p { color: #002D5E !important; font-weight: bold !important; }
    div.stButton > button {
        background-color: #E1E8F0 !important;
        color: #002D5E !important;
        border: 2px solid #002D5E !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        width: 100% !important;
        height: 50px !important;
    }
    [data-testid="stSidebar"] .stMarkdown p, [data-testid="stSidebar"] label { color: #FFFFFF !important; }
    </style>
    """, unsafe_allow_html=True)

# 4. BACKEND (CONEXÃO GITHUB)
def carregar_sistema():
    colunas = ["Passageiro", "Motorista", "Data", "Trajeto", "Obs Itinerário", "Hotel (R$)", "Combustível (R$)", "Aéreo (R$)", "Outros (R$)", "Total (R$)"]
    try:
        g = Github(st.secrets["GITHUB_TOKEN"])
        repo = g.get_repo("yaramaia122-lgtm/logistica-aura")
        contents = repo.get_contents("dados_logistica.csv")
        df = pd.read_csv(io.StringIO(contents.decoded_content.decode()))
        for col in colunas:
            if col not in df.columns: df[col] = 0.0 if "R$" in col else ""
        return df, contents.sha, repo
    except Exception as e:
        return pd.DataFrame(columns=colunas), None, None

df, sha, repo = carregar_sistema()

# 5. SIDEBAR
with st.sidebar:
    st.markdown("<br>", unsafe_allow_html=True)
    logo_path = "https://raw.githubusercontent.com/yaramaia122-lgtm/logistica-aura/main/logo.png"
    st.markdown(f'<div class="logo-container"><img src="{logo_path}" width="220"></div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    menu = st.radio("NAVEGAÇÃO:", ["📋 Agenda de Viagens", "📝 Programar Viagem", "💰 Financeiro"])

# 6. TELAS

if menu == "📋 Agenda de Viagens":
    st.title("📋 Agenda de Viagens")
    if not df.empty:
        st.dataframe(df[["Passageiro", "Motorista", "Data", "Trajeto", "Obs Itinerário"]], use_container_width=True)
    else:
        st.info("Nenhum registro encontrado.")

elif menu == "📝 Programar Viagem":
    st.title("📝 Programar Viagem")
    
    # IMPORTANTE: Criamos um container para mensagens de erro/sucesso fora do form
    status_container = st.container()

    with st.form("form_v", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            nome = st.text_input("Nome do Passageiro *").upper()
            motorista = st.selectbox("Motorista Designado", ["Ilson", "Antonio", "Outro"])
            v_hotel = st.number_input("Valor Hotel (R$)", min_value=0.0, step=1.0)
            v_aereo = st.number_input("Valor Aéreo (R$)", min_value=0.0, step=1.0)
        with c2:
            data = st.date_input("Data da Viagem", datetime.now())
            trajeto = st.selectbox("Itinerário Principal", ["P. Lacerda x Cuiabá", "Interno", "Outro"])
            v_comb = st.number_input("Valor Combustível (R$)", min_value=0.0, step=1.0)
            v_outros = st.number_input("Outros Custos (R$)", min_value=0.0, step=1.0)
        
        # Campo de descrição inteligente
        label_obs = "Descreva o Itinerário (Campo Obrigatório)" if trajeto == "Outro" else "Observações Adicionais (Opcional)"
        obs_itinerario = st.
