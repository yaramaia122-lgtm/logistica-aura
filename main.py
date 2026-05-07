import streamlit as st
import pandas as pd
from github import Github, Auth
import io
from datetime import datetime, timedelta

# --- 1. CONFIGURAÇÕES E ESTILO (SEM PRETO / AZUL CLARO / DESIGN AURA) ---
st.set_page_config(page_title="AURA APOENA LOGISTICS", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #F0F8FF; }
    [data-testid="stSidebar"] { background-color: #002D5E !important; }
    label, p, span { color: #002D5E !important; font-weight: 700; }
    
    /* INPUTS E DROPDOWNS: AZUL CLARO SEM PRETO */
    .stTextInput input, .stSelectbox div[data-baseweb="select"], 
    .stNumberInput input, .stDateInput input {
        background-color: #E3F2FD !important;
        color: #002D5E !important;
        border: 2px solid #90CAF9 !important;
        border-radius: 8px !important;
    }
    div[data-baseweb="popover"] ul { background-color: #FFFFFF !important; }
    div[role="option"] { color: #002D5E !important; background-color: #FFFFFF !important; }
    div[role="option"]:hover { background-color: #BBDEFB !important; }

    /* CABEÇALHOS DA AGENDA (CORES DA IMAGEM) */
    .header-trecho {
        background-color: #002D5E; color: white; padding: 10px;
        text-align: center; font-weight: bold; border-radius: 5px 5px 0 0;
    }
    .header-vermelho {
        background-color: #FF7F50; color: white; padding: 10px;
        text-align: center; font-weight: bold; border-radius: 5px 5px 0 0;
    }
    
    /* TABELAS */
    .stDataFrame { border: 1px solid #90CAF9; border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

# --- 2. BANCO DE DADOS E LISTA DE CENTRO DE CUSTO ---
CC_LISTA = [
    "210301 - Moagem", "210401 - Planta", "210801 - Laboratório", "210002 - Manutenção Mecânica Planta",
    "210405 - Lixiviação / Cianetação", "210001 - Administração Planta", "211001 - Manutenção Elétrica Planta",
    "211003 - Oficina Manutenção Planta", "210201 - Britagem Primária", "210604 - Fundição", "210501 - Almoxarifado",
    "320401 - Controladoria e Contabilidade", "310701 - Serviços Gerais", "320601 - Célula de Gestão de Contratos",
    "320101 - Suprimentos", "311101 - Tecnologia da Informação", "311202 - Care and Maintenance SF",
    "330102 - Apoena Corporativo", "311203 - Care and Maintenance PPQ", "311301 - Meio Ambiente",
    "310801 - Segurança Patrimonial", "310301 - PCP", "320201 - Gerência Geral", "310508 - Comunidades",
    "310101 - RH / Administrativo", "320301 - Recursos Humanos", "310902 - Campo", "310904 - Exploração EPP",
    "121101 - Geologia Operacional - Mina Ernesto", "121102 - Planejamento e Topografia - Mina Ernesto",
    "151101 - Geologia Operacional - Mina Nosde", "210502 - Saúde", "150101 - Administração de Mina Ernesto"
]

@st.cache_data(ttl=5)
def carregar_dados():
    try:
        tk = st.secrets["GITHUB_TOKEN"]
        rp = Github(auth=Auth.Token(tk)).get_repo("yaramaia122-lgtm/logistica-aura")
        def ler(arq, cols):
            try:
                c = rp.get_contents(arq)
                d = pd.read_csv(io.StringIO(c.decoded_content.decode()))
                for cl in cols:
                    if cl not in d.columns: d[cl] = ""
                return d, c.sha
            except: return pd.DataFrame(columns=cols), None

        dv, sv = ler("dados_logistica.csv", ["Passageiro","Motorista","Data","Hora_Saida","Trajeto","Status","Centro_Custo","Hotel_V","Comb_V","Aereo_V","Outros_V","Total","Voo","Voo_Hora","Hotel","Hospedagem"])
        du, su = ler("usuarios.csv", ["Usuario","Senha","Perfil","TrocarSenha"])
        do, so = ler("observacoes.csv", ["Data","Observacao"])
        return dv, sv, du, su, do, so, rp
    except: return None

banco = carregar_dados()
if not banco: st.stop()
df, s_v, df_u, s_u, df_o, s_o, repo = banco

# --- 3. LOGIN E GESTÃO DE USUÁRIOS ---
if 'logado' not in st.session_state: st.session_state['logado'] = False

if not st.session_state['logado']:
    st.markdown("<style>.stApp { background-color: #002D5E !important; } label { color: white !important; }</style>", unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.image("https://raw.githubusercontent.com/yaramaia122-lgtm/logistica-aura/main/logo.png", width=280)
        st.markdown("<h2 style='color:white; text-align:center;'>LOGISTICAS</h2>", unsafe_allow_html=True)
        with st.form("login"):
            u = st.text_input("Usuário").strip()
            p = st.text_input("Senha", type="password")
            if st.form_submit_button("ACESSAR SISTEMA"):
                user_data = df_u[(df_u['Usuario'] == u) & (df_u['Senha'] == p)]
                if not user_data.empty:
                    st.session_state['logado'] = True
                    st.session_state['user'] = u
                    st.session_state['perfil'] = user_data.iloc[0]['Perfil']
                    st.rerun()
                else: st.error("Incorreto.")
else:
