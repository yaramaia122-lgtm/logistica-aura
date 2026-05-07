import streamlit as st
import pandas as pd
from github import Github, Auth
import io
import os
from datetime import datetime, timedelta

# 1. ESTILO MODERNO (DESIGN AURA 2.0)
st.set_page_config(page_title="AURA APOENA", layout="wide")

st.markdown("""
<style>
    /* Fundo Principal e Sidebar */
    .stApp { background-color: #F4F7F9 !important; }
    [data-testid="stSidebar"] { background-color: #002D5E !important; border-right: 1px solid #003a7a; }
    
    /* Fontes e Títulos */
    h1, h2, h3 { color: #002D5E !important; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    
    /* DESIGN DA TELA DE LOGIN (MODERNO) */
    .login-container {
        background: #002D5E;
        padding: 40px;
        border-radius: 15px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.3);
    }
    
    /* INPUTS BRANCOS COM IDENTIFICAÇÃO CLARA */
    div[data-testid="stForm"] .stTextInput input {
        background-color: #FFFFFF !important;
        color: #002D5E !important;
        border: 2px solid #E0E6ED !important;
        border-radius: 10px !important;
        height: 50px !important;
        padding: 10px 15px !important;
    }
    
    /* BOTÃO ACESSAR (MODERNO COM HOVER) */
    div.stButton > button {
        background-color: #FFFFFF !important;
        color: #002D5E !important;
        font-weight: 700 !important;
        border-radius: 10px !important;
        border: none !important;
        height: 50px !important;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.2);
        background-color: #f8f9fa !important;
    }

    /* AGENDA (VISUAL CLEAN) */
    .obs-header {
        background: linear-gradient(90deg, #E75945, #ff7e6b);
        color: white; text-align: center;
        padding: 12px; font-weight: 600; border-radius: 10px 10px 0 0;
    }
    .obs-row { display: flex; border: 1px solid #E0E6ED; border-top: none; background: white; }
    .obs-day { width: 150px; padding: 15px; background-color: #F8FAFC; border-right: 1px solid #E0E6ED; font-weight: 600; color: #002D5E; }
    .obs-content { flex-grow: 1; padding: 15px; color: #475569; min-height: 50px; }
</style>
""", unsafe_allow_html=True)

# 2. CONEXÃO COM GITHUB
@st.cache_data(ttl=5)
def carregar_dados():
    try:
        tk = st.secrets["GITHUB_TOKEN"]
        rp = Github(auth=Auth.Token(tk)).get_repo("yaramaia122-lgtm/logistica-aura")
        def ler(arq, cols):
            try:
                c = rp.get_contents(arq)
                df_l = pd.read_csv(io.StringIO(c.decoded_content.decode()))
                for cl in cols:
                    if cl not in df_l.columns: df_l[cl] = ""
                return df_l, c.sha
            except: return pd.DataFrame(columns=cols), None

        cv = ["Passageiro", "Motorista", "Data", "Trajeto", "Status", "Centro_Custo", 
              "Hotel_V", "Comb_V", "Aereo_V", "Outro_V", "Total", "Voo", "Voo_Hora", "Hotel", "Hora_Saida"]
        df_v, sh_v = ler("dados_logistica.csv", cv)
        df_u, sh_u = ler("usuarios.csv", ["Usuario", "Senha"])
        df_o, sh_o = ler("observacoes.csv", ["Data", "Observacao"])
        return df_v, sh_v, df_u, sh_u, df_o, sh_o, rp
    except: return None

res = carregar_dados()
if not res: st.stop()
df, s_v, df_u, s_u, df_o, s_o, repo = res

# 3. TELA DE LOGIN (ESTILO D11B80 MODERNO)
if
