import streamlit as st
import pandas as pd
from github import Github, Auth
import io
import os
from datetime import datetime, timedelta

# 1. CONFIGURAÇÕES, ESTILO E IDENTIDADE
APP_NAME = "AURA APOENA LOGISTICS"
st.set_page_config(page_title=APP_NAME, layout="wide")

st.markdown(f"""
<style>
    .stApp {{ background-color: #FFFFFF !important; }}
    [data-testid="stSidebar"] {{ background-color: #002D5E !important; }}
    h1, h2, h3, label, p {{ color: #002D5E !important; font-weight: 700; }}
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] label, [data-testid="stSidebar"] span {{ color: #FFFFFF !important; }}
    
    div.stButton > button, div[data-testid="stForm"] button {{
        background-color: #FFFFFF !important; border: 2px solid #002D5E !important;
        border-radius: 8px !important; color: #002D5E !important;
        height: 45px !important; width: 100% !important; font-weight: 900 !important;
    }}
    
    .obs-header {{
        background-color: #E75945; color: white; text-align: center;
        padding: 10px; font-weight: bold; border: 1px solid #ddd; border-radius: 5px 5px 0 0;
    }}
    .obs-row {{ display: flex; border: 1px solid #ddd; border-top: none; }}
    .obs-day {{
        width: 140px; padding: 12px; background-color: #f8f9fa;
        border-right: 1px solid #ddd; font-weight: bold; font-size: 14px;
    }}
    .obs-content {{ flex-grow: 1; padding: 12px; color: #333; min-height: 45px; }}
</style>
""", unsafe_allow_html=True)

# 2. CONEXÃO COM GITHUB (BANCO DE DADOS)
@st.cache_data(ttl=5)
def conectar_banco():
    try:
        tk = st.secrets["GITHUB_TOKEN"]
        rp = Github(auth=Auth.Token(tk)).get_repo("yaramaia122-lgtm/logistica-aura")
        def carregar(arq, cols):
            try:
                c = rp.get_contents(arq)
                return pd.read_csv(io.StringIO(c.decoded_content.decode())), c.sha
            except: return pd.DataFrame(columns=cols), None

        cv = ["Passageiro", "Motorista", "Data", "Trajeto", "Status", "Centro_Custo", 
              "Hotel_V", "Comb_V", "Aereo_V", "Outro_V", "Total", "Voo", "Voo_Hora", "Hotel"]
        df_v, sh_v = carregar("dados_logistica.csv", cv)
        df_u, sh_u = carregar("usuarios.csv", ["Usuario", "Senha", "Perfil"])
        df_o, sh_o = carregar("observacoes.csv", ["Data", "Observacao"])
        return df_v, sh_v, df_u, sh_u, df_
