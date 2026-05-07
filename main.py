import streamlit as st
import pandas as pd
from github import Github, Auth
import io
from datetime import datetime, timedelta

# --- 1. CONFIGURAÇÕES E IDENTIDADE VISUAL (Design d11b80) ---
st.set_page_config(page_title="AURA APOENA", layout="wide")

st.markdown("""
<style>
    /* Estilo Geral */
    .stApp { background-color: #F4F7F9; }
    [data-testid="stSidebar"] { background-color: #002D5E !important; }
    h1, h2, h3, label { color: #002D5E !important; font-weight: 700; }
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] label { color: white !important; }

    /* Rótulos e Inputs da Tela de Login */
    .lbl-login { color: #FFFFFF !important; font-weight: 600; margin-bottom: 5px; }
    div[data-testid="stForm"] .stTextInput input {
        background-color: #FFFFFF !important; color: #002D5E !important;
        border-radius: 8px !important; border: 1px solid #E2E8F0 !important;
    }

    /* Botão Acessar Sistema */
    div.stButton > button {
        background-color: #FFFFFF !important; color: #002D5E !important;
        font-weight: 800 !important; border-radius: 10px !important;
        height: 48px !important; width: 100% !important; border: none !important;
    }

    /* Cabeçalho da Agenda (Vermelho Aura) */
    .header-obs {
        background-color: #E75945; color: white; padding: 12px;
        text-align: center; font-weight: bold; border-radius: 10px 10px 0 0;
    }
    .row-obs { display: flex; border: 1px solid #DDD; border-top: none; background: white; }
    .col-dia { width: 150px; padding: 10px; background: #F8F9FA; border-right: 1px solid #DDD; font-weight: bold; }
    .col-txt { flex-grow: 1; padding: 10px; color: #333; }
</style>
""", unsafe_allow_html=True)

# --- 2. GESTÃO DE DADOS (GITHUB) ---
@st.cache_data(ttl=5)
def carregar_sistema():
    try:
        token = st.secrets["GITHUB_TOKEN"]
        repo = Github(auth=Auth.Token(token)).get_repo("yaramaia122-lgtm/logistica-aura")
        
        def baixar(arquivo, colunas):
            try:
                conteudo = repo.get_contents(arquivo)
                df = pd
