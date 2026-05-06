import streamlit as st
import pandas as pd
from github import Github, Auth
import io
import os
from datetime import datetime, timedelta

# ==========================================================
# 1. CONFIGURAÇÕES TÉCNICAS E CSS (VISUAL TRAVADO)
# ==========================================================
st.set_page_config(page_title="Aura Apoena Logistics", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #FFFFFF !important; }
    [data-testid="stSidebar"] { background-color: #002D5E !important; }
    h1, h2, h3, label, p { color: #002D5E !important; font-weight: 700; }
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] label, [data-testid="stSidebar"] span { color: #FFFFFF !important; }
    
    /* BOTÃO PADRÃO: FUNDO BRANCO / LETRA AZUL MARINHO */
    div.stButton > button, div[data-testid="stForm"] button {
        background-color: #FFFFFF !important;
        border: 2px solid #002D5E !important;
        border-radius: 8px !important;
        height: 50px !important;
        width: 100% !important;
    }
    div.stButton > button p, div[data-testid="stForm"] button p {
        color: #002D5E !important;
        font-weight: 900 !important;
    }
    div.stButton > button:hover { background-color: #002D5E !important; }
    div.stButton > button:hover p { color: #FFFFFF !important; }
    
    .obs-card { background-color: #E75945 !important; color: white !important; padding: 15px; border-radius: 8px; margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

# ==========================================================
# 2. MOTOR DE DADOS (GITHUB)
# ==========================================================
@st.cache_data(ttl=5)
def carregar_bancos():
    try:
        token = st.secrets["GITHUB_TOKEN"]
        auth = Auth.Token(token)
        g = Github(auth=auth)
        repo = g.get_repo("yaramaia122-lgtm/logistica-aura")
        
        def ler_arquivo(nome, colunas):
            try:
                c = repo.get_contents(nome)
                return pd.read_csv(io.StringIO(c.decoded_content.decode())), c.sha
            except:
                return pd.DataFrame(columns=colunas), None

        df_v, sha_v = ler_arquivo("dados_logistica.csv", ["Passageiro", "Motorista", "Data", "Trajeto", "Status", "Hotel_Valor", "Combustivel_Valor", "Aereo_Valor", "Outros_Valor", "Total", "Voo_Cia", "Hora_Voo", "Data_Voo", "Local_Hotel", "Hora_Saida"])
        df_u, sha_u = ler_arquivo("usuarios.csv", ["Usuario", "Senha", "Perfil"])
        df_o, sha_o = ler_arquivo("observacoes.csv", ["Data", "Observacao"])
        
        return df_v, sha_v, df_u, sha_u, df_o, sha_o, repo
    except:
        return None

banco = carregar_bancos()
if banco:
    df, sha_v, df_u, sha_u, df_o, sha_o, repo = banco
else:
    st.error("Erro Crítico: Verifique o GITHUB_TOKEN nos Secrets.")
    st.stop()

# ==========================================================
# 3. MÓDULO DE ACESSO (LOGIN)
# ==========================================================
if 'logado' not in st.session_state: st.session_state['logado'] = False

if not st.session_state['logado']:
    st.markdown("<style>.stApp { background-color: #002D5E !important; }</style>", unsafe_allow_html=True)
    c1, col_login, c3 = st.columns([1, 1.2, 1])
    with col_login:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.image("https://raw.githubusercontent.com/yaramaia122-lgtm/logistica-aura/main/logo.png", width=250)
        with st.form("f_login"):
            st.markdown("<h3 style='color:white; text-align:center;'>PORTAL DE LOGÍSTICA</h3>", unsafe_allow_html=True)
            u = st.text_input("Usuário")
            s = st.text_input("Senha", type="password")
            if st.form_submit_button("ENTRAR NO SISTEMA"):
                if not df_u[(df_u['Usuario'] == u) & (df_u['Senha'] == s)].empty:
                    st.session_state['logado'] = True
                    st.rerun()
                else: st.error("Acesso Negado")
else:
    # ==========================================================
    # 4. SISTEMA PRINCIPAL (MÓDULOS ANALISADOS)
    # ==========================================================
    with st.sidebar:
        st.image("https://raw.githubusercontent.com/yaramaia122-lgtm/logistica-aura/main/logo.png", width=180)
        menu = st.radio("NAVEGAÇÃO", ["Agenda", "Programar Viagem", "Dashboard", "Administração"])
        if st.button("SAIR DO SISTEMA"):
            st.session_state['logado'] = False
            st.rerun()

    # --- MÓDULO: AGENDA ---
    if menu == "Agenda":
        st.title("📅 Agenda Logística")
        d_
