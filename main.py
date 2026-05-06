import streamlit as st
import pandas as pd
from github import Github, Auth
import io
import os
from datetime import datetime, timedelta

# ==========================================================
# 1. CONFIGURAÇÕES DE INTERFACE (CSS DEFINITIVO)
# ==========================================================
st.set_page_config(page_title="Aura Apoena Logistics", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #FFFFFF !important; }
    [data-testid="stSidebar"] { background-color: #002D5E !important; }
    h1, h2, h3, label, p { color: #002D5E !important; font-weight: 700; }
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] label, [data-testid="stSidebar"] span { color: #FFFFFF !important; }

    /* --- ESTILO DOS BOTÕES (PADRÃO YARA) --- */
    div.stButton > button, div[data-testid="stForm"] button {
        background-color: #FFFFFF !important;
        border: 2px solid #002D5E !important;
        border-radius: 8px !important;
        height: 50px !important;
        width: 100% !important;
    }

    /* FORÇAR TEXTO EM AZUL MARINHO NO FUNDO BRANCO */
    div.stButton > button p, div[data-testid="stForm"] button p {
        color: #002D5E !important;
        font-weight: 900 !important;
        font-size: 16px !important;
        margin: 0px !important;
    }

    /* INVERSÃO AO PASSAR O MOUSE */
    div.stButton > button:hover, div[data-testid="stForm"] button:hover {
        background-color: #002D5E !important;
    }
    div.stButton > button:hover p, div[data-testid="stForm"] button:hover p {
        color: #FFFFFF !important;
    }

    .stTextInput input, .stSelectbox div[data-baseweb="select"], .stDateInput input { 
        background-color: #F0F7FF !important; border: 2px solid #002D5E !important; color: #002D5E !important; 
    }
    .obs-header { background-color: #E75945 !important; color: white !important; text-align: center !important; padding: 10px !important; font-weight: bold !important; border-radius: 8px 8px 0px 0px; margin-bottom: -15px; }
</style>
""", unsafe_allow_html=True)

# ==========================================================
# 2. VARIÁVEIS E BANCO DE DADOS
# ==========================================================
if 'logado' not in st.session_state: st.session_state['logado'] = False
if 'usuario_atual' not in st.session_state: st.session_state['usuario_atual'] = ""

DIAS_SEMANA_PT = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"]
MESES_PT = {1:'jan', 2:'fev', 3:'mar', 4:'abr', 5:'mai', 6:'jun', 7:'jul', 8:'ago', 9:'set', 10:'out', 11:'nov', 12:'dez'}

@st.cache_data(ttl=5)
def carregar_bancos():
    cols_v = ["Passageiro", "Motorista", "Data", "Semana", "Hora_Saida", "Trajeto", "Voo_Cia_Num", "Hora_Voo", "Data_Voo", "Local_Hotel", "Centro de Custo", "Status", "Hotel_Valor", "Combustivel_Valor", "Aereo_Valor", "Outros_Valor", "Total", "Usuario_Criador"]
    try:
        token = st.secrets["GITHUB_TOKEN"]
        auth = Auth.Token(token)
        g = Github(auth=auth)
        repo = g.get_repo("yaramaia122-lgtm/logistica-aura")
        
        try:
            cv = repo.get_contents("dados_logistica.csv")
            df_v = pd.read_csv(io.StringIO(cv.decoded_content.decode()))
            sha_v = cv.sha
            # Correção técnica: Garantir colunas sem erro de sintaxe
            for c in cols_v:
                if c not in df_v.columns:
                    df_v[c] = 0.0 if "_Valor" in c or c == "Total" else ""
        except:
            df_v = pd.DataFrame(columns=cols_v); sha_v = None

        try:
            cu = repo.get_contents("usuarios.csv")
            df_u = pd.read_csv(io.StringIO(cu.decoded_content.decode()))
            sha_u = cu.sha
        except:
            df_u = pd.DataFrame([["yara.chaves", "aura123", "Administrador", "Ativo", "Sim"]], columns=["Usuario", "Senha", "Perfil", "Status", "Primeiro_Acesso"])
            repo.create_file("usuarios.csv", "Init", df_u.to_csv(index=False))
            sha_u = repo.get_contents("usuarios.csv").sha

        try:
            co = repo.get_contents("observacoes.csv")
            df_o = pd.read_csv(io.StringIO(co.decoded_content.decode()))
            sha_o = co.sha
        except:
            df_o = pd.DataFrame(columns=["Data", "Observacao"]); sha_o = None

        return df_v, sha_v, df_u, sha_u, df_o, sha_o, repo
    except:
        return pd.DataFrame(), None, pd.DataFrame(), None, pd.DataFrame(), None, None

df, sha_viagens, df_usuarios, sha_usuarios, df_obs, sha_obs, repo = carregar_bancos()

# ==========================================================
# 3. LÓGICA DE TELAS
# ==========================================================
if not st.session_state['logado']:
    st.markdown("<style>.stApp { background-color: #002D5E !important; } h2 { color: white !important; }</style>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.image("https://raw.githubusercontent.com/yaramaia122-lgtm/logistica-aura/main/logo.png", width=220)
        st.markdown("<h2 style='text-align: center;'>Login</h2>", unsafe_allow_html=True)
        with st.form("f_login"):
            u = st.text_input("Usuário")
            s = st.text_input("Senha", type="password")
            if st.form_submit_button("ENTRAR NO SISTEMA"):
                user_match = df_usuarios[(df_usuarios['Usuario'] == u) & (df_usuarios['Senha'] == s)]
                if not user_match.empty:
                    st.session_state['logado'], st.session_state['usuario_atual'] = True, u
                    st.rerun()
                else: st.error("Erro de login.")
else:
    with st.sidebar:
        st.image("https://raw.githubusercontent.com/yaramaia122-lgtm/logistica-aura/main/logo.png", width=180)
        menu = st.radio("NAVEGAÇÃO", ["Agenda", "Programar Viagem", "Administração"])
        if st.button("SAIR"): st.session_state['logado'] = False; st.rerun()

    if menu == "Agenda":
        st.title("Agenda de Viagens")
        d_sel = st.date_input("Semana:", datetime.now().date())
        ini = d_sel - timedelta(days=d_sel.weekday()); fim = ini + timedelta(days=6)
        if not df.empty:
            df['D_Obj'] = pd.to_datetime(df['Data'], format='%d/%m/%Y', errors='coerce').dt.date
            df_s = df[(df['D_Obj'] >= ini) & (df['D_Obj'] <= fim) & (df['Status'] != "Cancelada")]
            for t in sorted(df_s['Trajeto'].unique()):
                st.markdown(f"### 📍 {t}")
                st.dataframe(df_s[df_s['Trajeto']==t][["Passageiro", "Semana", "Data", "Hora_Saida", "Voo_Cia_Num", "Hora_Voo", "Data_Voo", "Local_Hotel", "Motorista"]], use_container_width=True, hide_index=True)

    elif menu == "Programar Viagem":
        st.title("Nova Programação")
        with st.form("f_add", clear_on_submit=True):
            c1, c2 = st.columns(2)
            px = c1.text_input("Passageiro").upper()
            mt = c1.selectbox("Motorista", ["Ilson", "Antonio", "Vagno", "Cido", "Outro"])
            tj = c1.
