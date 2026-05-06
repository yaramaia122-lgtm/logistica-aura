import streamlit as st
import pandas as pd
from github import Github, Auth
import io
from datetime import datetime, timedelta

# 1. ESTILO, CORES E NOME DO APP
APP_NAME = "AURA APOENA LOGISTICS"
st.set_page_config(page_title=APP_NAME, layout="wide")

st.markdown(f"""
<style>
    .stApp {{ background-color: #FFFFFF !important; }}
    [data-testid="stSidebar"] {{ background-color: #002D5E !important; }}
    h1, h2, h3, label, p {{ color: #002D5E !important; font-weight: 700; }}
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] label, [data-testid="stSidebar"] span {{ color: #FFFFFF !important; }}
    
    /* BOTÃO PADRÃO */
    div.stButton > button, div[data-testid="stForm"] button {{
        background-color: #FFFFFF !important;
        border: 2px solid #002D5E !important;
        border-radius: 8px !important;
        height: 48px !important;
        width: 100% !important;
    }}
    div.stButton > button p, div[data-testid="stForm"] button p {{
        color: #002D5E !important; font-weight: 900;
    }}
    
    /* TABELA DE OBSERVAÇÕES ESTILO EXEMPLO */
    .obs-header {{
        background-color: #E75945;
        color: white;
        text-align: center;
        padding: 5px;
        font-weight: bold;
        border: 1px solid #ddd;
    }}
    .obs-row {{
        display: flex;
        border: 1px solid #ddd;
    }}
    .obs-day {{
        width: 150px;
        padding: 10px;
        background-color: #f9f9f9;
        border-right: 1px solid #ddd;
        font-weight: bold;
    }}
    .obs-content {{
        flex-grow: 1;
        padding: 10px;
    }}
</style>
""", unsafe_allow_html=True)

# 2. CONEXÃO GITHUB
@st.cache_data(ttl=5)
def carregar_dados():
    try:
        tk = st.secrets["GITHUB_TOKEN"]
        repo = Github(auth=Auth.Token(tk)).get_repo("yaramaia122-lgtm/logistica-aura")
        def ler(arq, cols):
            try:
                c = repo.get_contents(arq)
                return pd.read_csv(io.StringIO(c.decoded_content.decode())), c.sha
            except: return pd.DataFrame(columns=cols), None
        df_v, sh_v = ler("dados_logistica.csv", ["Passageiro","Motorista","Data","Trajeto","Status","Centro_Custo","Hotel_V","Comb_V","A
