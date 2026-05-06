import streamlit as st
import pandas as pd
from github import Github, Auth
import io
import os
from datetime import datetime, timedelta

# 1. CONFIGURAÇÕES DE INTERFACE E DESTRAVAMENTO DE CORES
st.set_page_config(page_title="Aura Apoena Logistics", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #FFFFFF !important; }
    [data-testid="stSidebar"] { background-color: #002D5E !important; }
    h1, h2, h3, label, p { color: #002D5E !important; font-weight: 700; }
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] label, [data-testid="stSidebar"] span { color: #FFFFFF !important; }

    /* --- BLOQUEIO DE CORES DOS BOTÕES --- */
    div.stButton > button {
        background-color: #FFFFFF !important;
        border: 2px solid #002D5E !important;
        border-radius: 8px !important;
        height: 50px !important;
        width: 100% !important;
    }

    /* Força o texto para Azul Marinho (Ignora o tema do sistema) */
    div.stButton > button p {
        color: #002D5E !important;
        fill: #002D5E !important;
        font-weight: 900 !important;
        font-size: 16px !important;
    }

    div.stButton > button:hover {
        background-color: #002D5E !important;
    }
    
    div.stButton > button:hover p {
        color: #FFFFFF !important;
        fill: #FFFFFF !important;
    }

    .stTextInput input, .stSelectbox div[data-baseweb="select"] { 
        background-color: #F0F7FF !important; border: 2px solid #002D5E !important; color: #002D5E !important; 
    }
</style>
""", unsafe_allow_html=True)

# 2. VARIÁVEIS DE SESSÃO
if 'logado' not in st.session_state: st.session_state['logado'] = False
if 'usuario_atual' not in st.session_state: st.session_state['usuario_atual'] = ""

DIAS_SEMANA_PT = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"]

# 3. CONEXÃO SEGURA COM O BANCO
@st.cache_data(ttl=5)
def carregar_dados():
    try:
        token = st.secrets["GITHUB_TOKEN"]
        auth = Auth.Token(token)
        g = Github(auth=auth)
        repo = g.get_repo("yaramaia122-lgtm/logistica-aura")
        
        # Carregar Viagens
        try:
            cv = repo.get_contents("dados_logistica.csv")
            df_v = pd.read_csv(io.StringIO(cv.decoded_content.decode()))
            sha_v = cv.sha
        except:
            df_v = pd.DataFrame(columns=["Passageiro", "Motorista", "Data", "Semana", "Hora_Saida", "Trajeto", "Total", "Status"])
            sha_v = None

        # Carregar Usuários
        try:
            cu = repo.get_contents("usuarios.csv")
            df_u = pd.read_csv(io.StringIO(cu.decoded_content.decode()))
            sha_u = cu.sha
        except:
            df_u = pd.DataFrame([["yara.chaves", "aura123", "Administrador"]], columns=["Usuario", "Senha", "Perfil"])
            sha_u = None

        return df_v, sha_v, df_u, sha_u, repo
    except:
        return pd.DataFrame(), None, pd.DataFrame(), None, None

df, sha_v, df_u, sha_u, repo = carregar_dados()

# 4. LÓGICA DE TELAS
if not st.session_state['logado']:
    st.markdown("<style>.stApp { background-color: #002D5E !important; }</style>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1.2, 1])
    with c2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.image("https://raw.githubusercontent.com/yaramaia122-lgtm/logistica-aura/main/logo.png", width=220)
        st.markdown("<h2 style='text-align: center; color: white;'>Acesso ao Portal</h2>", unsafe_allow_html=True)
        with st.form("login_form"):
            user = st.text_input("Usuário")
            password = st.text_input("Senha", type="password")
            if st.form_submit_button("ENTRAR NO SISTEMA"):
                if not df_u.empty:
                    match = df_u[(df_u['Usuario'] == user) & (df_u['Senha'] == password)]
                    if not match.empty:
                        st.session_state['logado'] = True
                        st.session_state['usuario_atual'] = user
                        st.rerun()
                    else: st.error("Incorreto.")
else:
    # --- APP LOGADO ---
    with st.sidebar:
        st.image("https://raw.githubusercontent.com/yaramaia122-lgtm/logistica-aura/main/logo.png", width=180)
        menu = st.radio("NAVEGAÇÃO", ["Agenda", "Programar", "Dashboard", "Administração"])
        if st.button("SAIR"): 
            st.session_state['logado'] = False
            st.rerun()

    if menu == "Agenda":
        st.title("Agenda de Viagens")
        d_sel = st.date_input("Ver semana de:", datetime.now().date())
        ini = d_sel - timedelta(days=d_sel.weekday())
        fim = ini + timedelta(days=6)
        
        if not df.empty:
            df['Data_Dt'] = pd.to_datetime(df['Data'], format='%d/%m/%Y', errors='coerce').dt.date
            df_s = df[(df['Data_Dt'] >= ini) & (df['Data_Dt'] <= fim
