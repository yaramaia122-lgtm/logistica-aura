import streamlit as st
import pandas as pd
from github import Github
import io
from datetime import datetime

# 1. CONFIGURAÇÃO DE ALTO NÍVEL
st.set_page_config(page_title="Aura Apoena Logistics", layout="wide")

# 2. DESIGN "CLEAN" (AZUL CLARO, MARINHO E PRETO)
# Foquei em remover sombras internas que deixam o app com aspecto de "velho"
st.markdown("""
    <style>
    /* Fundo principal limpo */
    .stApp { background-color: #FFFFFF; }
    
    /* Sidebar Marinho Profissional */
    [data-testid="stSidebar"] {
        background-color: #002D5E !important;
        border-right: 1px solid #E1E8F0;
    }
    
    /* Efeito de Sombra Suave na Logo Aura */
    [data-testid="stSidebar"] [data-testid="stImage"] img {
        filter: drop-shadow(0px 8px 12px rgba(0,0,0,0.5));
        margin-bottom: 20px;
    }

    /* CAIXAS DE ENTRADA: Azul Gelo (#F0F7FF) com texto Preto Puro (#000000) */
    .stTextInput input, .stSelectbox div[data-baseweb="select"], .stDateInput input, .stNumberInput input {
        background-color: #F0F7FF !important; 
        border: 1px solid #002D5E !important;
        color: #000000 !important;
        border-radius: 6px !important;
        font-size: 16px !important;
    }
    
    /* Forçar texto preto em listas de seleção */
    div[data-baseweb="select"] span { color: #000000 !important; }

    /* BOTÕES: Azul Claro com Texto Marinho (Alta Visibilidade) */
    div.stButton > button {
        background-color: #E1E8F0 !important;
        color: #002D5E !important;
        border: 1px solid #002D5E !important;
        font-weight: 700 !important;
        border-radius: 8px !important;
        height: 48px !important;
        transition: 0.3s;
    }
    div.stButton > button:hover {
        background-color: #002D5E !important;
        color: #FFFFFF !important;
    }

    /* Títulos e Labels */
    h1, h2, h3 { color: #002D5E !important; font-family: 'Segoe UI', Tahoma, sans-serif; }
    label { color: #002D5E !important; font-weight: 600 !important; margin-bottom: 5px !important; }
    
    /* Texto Sidebar em Branco para contraste */
    [data-testid="stSidebar"] .stMarkdown p, [data-testid="stSidebar"] label { color: #FFFFFF !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. CONEXÃO SEGURA (GITHUB)
def carregar_dados():
    colunas = ["Passageiro", "Motorista", "Data", "Trajeto", "Obs Itinerario", "Hotel", "Combustivel", "Aereo", "Outros", "Total"]
    try:
        g = Github(st.secrets["GITHUB_TOKEN"])
        repo = g.get_repo("yaramaia122-lgtm/logistica-aura")
        contents = repo.get_contents("dados_logistica.csv")
        df = pd.read_csv(io.StringIO(contents.decoded_content.decode()))
        # Garante que colunas novas não quebrem o app
        for col in colunas:
            if col not in df.columns: df[col] = 0.0 if col in ["Hotel", "Combustivel", "Aereo", "Outros", "Total"] else ""
        return df, contents.sha, repo
    except:
        return pd.DataFrame(columns=colunas), None, None

df, sha, repo = carregar_dados()

# 4. BARRA LATERAL
with st.sidebar:
    st.markdown("<br>", unsafe_allow_html=True)
    logo_path = "https://raw.githubusercontent.com/yaramaia122-lgtm/logistica-aura/main/logo.png"
    st.image(logo_path, width=230)
    st.markdown("
