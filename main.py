import streamlit as st
import pandas as pd
from github import Github, Auth
import io
import os
from datetime import datetime, timedelta

# 1. ESTILO AURA (DESIGN TELA D11B80 E AGENDA)
st.set_page_config(page_title="AURA APOENA", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #FFFFFF !important; }
    [data-testid="stSidebar"] { background-color: #002D5E !important; }
    h1, h2, h3, label, p { color: #002D5E !important; font-weight: 700; }
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] label { color: white !important; }
    
    /* INPUTS BRANCOS (TELA LOGIN) */
    div[data-testid="stForm"] .stTextInput input {
        background-color: #FFFFFF !important;
        color: #002D5E !important;
        border: 1px solid #002D5E !important;
    }
    
    /* BOTÃO ACESSAR */
    div.stButton > button {
        background-color: #FFFFFF !important; color: #002D5E !important;
        font-weight: 900 !important; border-radius: 8px !important;
        height: 45px !important; width: 100% !important;
    }

    /* AGENDA CABEÇALHO VERMELHO */
    .obs-header {
        background-color: #E75945; color: white; text-align: center;
        padding: 10px; font-weight: bold; border-radius: 5px 5px 0 0;
    }
    .obs-row { display: flex; border: 1px solid #ddd; border-top: none; }
    .obs-day { width: 140px; padding: 12px; background-color: #f8f9fa; border-right: 1px solid #ddd; font-weight: bold; }
    .obs-content { flex-grow: 1; padding: 12px; color: #333; min-height: 45px; }
</style>
""", unsafe_allow_html=True)

# 2. BANCO DE DADOS
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

        cols_v = ["Passageiro", "Motorista", "Data", "Trajeto", "Status", "Centro_Custo", 
                  "Hotel_V", "Comb_V", "Aereo_V", "Outro_V", "Total", "Voo", "Voo_Hora", "Hotel", "Hora_Saida"]
        df_v, sh_v = ler("dados_logistica.csv", cols_v)
        df_u, sh_u = ler("usuarios.csv", ["Usuario", "Senha"])
        df_o, sh_o = ler("observacoes.csv", ["Data", "Observacao"])
        return df_v, sh_v, df_u, sh_u, df_o, sh_o, rp
    except: return None

res = carregar_dados()
if not res: st.stop()
df, s_v, df_u, s_u, df_o, s_o, repo = res

# 3. LOGIN (DESIGN TELA D11B80)
if 'logado' not in st.session_state: st.session_state['logado'] = False

if not st.session_state['logado']:
    st.markdown("<style>.stApp { background-color: #002D5E !important; } label { color: white !important; }</style>", unsafe_allow_html=True)
    _, col_log, _ = st.columns([1, 1.2, 1])
    with col_log:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.image("https://raw.githubusercontent.com/yaramaia122-lgtm/logistica-aura/main/logo.png", width=280)
        st.markdown("<h2 style='color:white; text-align:center; letter-spacing: 5px;'>LOGISTICAS</h2>", unsafe_allow_html=True)
        with st.form("login_form"):
            user = st.text_input("usuario")
            pswd = st.text_input("senha", type="password")
            if st.form_submit_button("ACESSAR SISTEMA"):
                if not df_u[(df_u['Usuario'] == user) & (df_u['Senha'] == pswd)].empty:
                    st.session_state['logado'] = True
                    st.rerun()
                else: st.error("Dados incorretos.")
else:
    # 4. SISTEMA
    with st.sidebar:
        st.image("https://raw.githubusercontent.com/yaramaia122-lgtm/logistica-aura/main/logo.png", width=180)
        # Nomes simplificados no código para evitar cortes de caractere especial
        aba = st.radio("MENU", ["Agenda", "Programar", "Dashboard", "Admin"])
        if st.button("SAIR"): 
            st.session_state['logado'] = False
            st.rerun()

    if aba == "Agenda":
        st.title("📅 Agenda Semanal")
        st.markdown('<div class="obs-header">Observações</div>', unsafe_allow_html=True)
        dias = ["Segunda-Feira", "Terça-Feira", "Quarta-Feira", "Quinta-Feira", "Sexta-Feira", "Sábado", "Domingo"]
        hoje = datetime.now()
        segunda = hoje - timedelta(days=hoje.weekday
