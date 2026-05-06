import streamlit as st
import pandas as pd
from github import Github, Auth
import io
import os
from datetime import datetime, timedelta

# ==========================================================
# 0. CONFIGURAÇÕES TÉCNICAS E ESTILO (PADRÃO YARA)
# ==========================================================
st.set_page_config(page_title="Aura Apoena Logistics", layout="wide")

# CSS para garantir que a letra do botão de login seja AZUL MARINHO no fundo BRANCO
st.markdown("""
<style>
    /* Estilo Geral */
    .stApp { background-color: #FFFFFF !important; }
    [data-testid="stSidebar"] { background-color: #002D5E !important; }
    h1, h2, h3, label, p { color: #002D5E !important; font-weight: 700; }
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] label, [data-testid="stSidebar"] span { color: #FFFFFF !important; }

    /* BOTÃO DE LOGIN E ENTRADA - FORÇANDO LETRA AZUL MARINHO */
    button[kind="primaryFormSubmit"], button[kind="secondaryFormSubmit"], .stButton > button {
        background-color: #FFFFFF !important;
        border: 2px solid #002D5E !important;
        border-radius: 8px !important;
        height: 50px !important;
        width: 100% !important;
    }

    /* ESSA É A LINHA QUE DESTRAVA O TEXTO */
    button[kind="primaryFormSubmit"] p, button[kind="secondaryFormSubmit"] p, .stButton > button p {
        color: #002D5E !important;
        font-weight: 900 !important;
        font-size: 16px !important;
    }

    /* Efeito de Inversão ao passar o mouse */
    button[kind="primaryFormSubmit"]:hover, .stButton > button:hover {
        background-color: #002D5E !important;
    }
    button[kind="primaryFormSubmit"]:hover p, .stButton > button:hover p {
        color: #FFFFFF !important;
    }

    /* Inputs */
    .stTextInput input, .stSelectbox div[data-baseweb="select"], .stDateInput input { 
        background-color: #F0F7FF !important; border: 2px solid #002D5E !important; color: #002D5E !important; 
    }
</style>
""", unsafe_allow_html=True)

# ==========================================================
# 1. INICIALIZAÇÃO DE VARIÁVEIS DE SESSÃO
# ==========================================================
if 'logado' not in st.session_state: st.session_state['logado'] = False
if 'usuario_atual' not in st.session_state: st.session_state['usuario_atual'] = ""
if 'perfil' not in st.session_state: st.session_state['perfil'] = ""
if 'precisa_trocar_senha' not in st.session_state: st.session_state['precisa_trocar_senha'] = False
if 'usuario_troca' not in st.session_state: st.session_state['usuario_troca'] = ""

DIAS_SEMANA_PT = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"]
MESES_PT = {1:'jan', 2:'fev', 3:'mar', 4:'abr', 5:'mai', 6:'jun', 7:'jul', 8:'ago', 9:'set', 10:'out', 11:'nov', 12:'dez'}

# ==========================================================
# 2. CARREGAMENTO DE DADOS (GITHUB)
# ==========================================================
@st.cache_data(ttl=5)
def carregar_bancos():
    cols_v = ["Passageiro", "Motorista", "Data", "Semana", "Hora_Saida", "Trajeto", "Voo_Cia_Num", "Hora_Voo", "Data_Voo", "Local_Hotel", "Centro de Custo", "Status", "Hotel_Valor", "Aereo_Valor", "Total", "Usuario_Criador"]
    cols_u = ["Usuario", "Senha", "Perfil", "Status", "Primeiro_Acesso"]
    
    try:
        token = st.secrets["GITHUB_TOKEN"]
        auth = Auth.Token(token)
        g = Github(auth=auth)
        repo = g.get_repo("yaramaia122-lgtm/logistica-aura")
        
        # Viagens
        try:
            cv = repo.get_contents("dados_logistica.csv")
            df_v = pd.read_csv(io.StringIO(cv.decoded_content.decode()))
            sha_v = cv.sha
        except:
            df_v = pd.DataFrame(columns=cols_v); sha_v = None

        # Usuários
        try:
            cu = repo.get_contents("usuarios.csv")
            df_u = pd.read_csv(io.StringIO(cu.decoded_content.decode()))
            sha_u = cu.sha
        except:
            df_u = pd.DataFrame([["yara.chaves", "aura123", "Administrador", "Ativo", "Sim"]], columns=cols_u)
            repo.create_file("usuarios.csv", "Init", df_u.to_csv(index=False))
            sha_u = repo.get_contents("usuarios.csv").sha

        # Observações
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
# 3. LOGICA DE TELA (LOGIN OU APP)
# ==========================================================
if not st.session_state['logado']:
    # Cor de fundo azul marinho para o login
    st.markdown("<style>.stApp { background-color: #002D5E !important; } h2 { color: white !important; }</style>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.image("https://raw.githubusercontent.com/yaramaia122-lgtm/logistica-aura/main/logo.png", width=220)
        st.markdown("<h2 style='text-align: center;'>Acesso Restrito</h2>", unsafe_allow_html=True)
        
        with st.form("form_login"):
            u = st.text_input("Usuário Corporativo")
            s = st.text_input("Senha", type="password")
            entrar = st.form_submit_button("ENTRAR NO SISTEMA")
            
            if entrar:
                user_match = df_usuarios[(df_usuarios['Usuario'] == u) & (df_usuarios['Senha'] == s)]
                if not user_match.empty:
                    st.session_state['logado'] = True
                    st.session_state['usuario_atual'] = u
                    st.session_state['perfil'] = user_match.iloc[0]['Perfil']
                    st.rerun()
                else:
                    st.error("Usuário ou senha inválidos.")

else:
    # --- APP PRINCIPAL ---
    with st.sidebar:
        st.image("https://raw.githubusercontent.com/yaramaia122-lgtm/logistica-aura/main/logo.png", width=180)
        menu = st.radio("MENU", ["Agenda", "Programar Viagem", "Administração"])
        if st.button("SAIR"):
            st.session_state['logado'] = False
            st.rerun()

    if menu == "Agenda":
        st.title("Agenda Operacional")
        d_sel = st.date_input("Semana:", datetime.now().date())
        ini = d_sel - timedelta(days=d_sel.weekday()); fim = ini + timedelta(days=6)
        
        if not df.empty:
            # Filtro e exibição das tabelas por trecho
            df['D_Obj'] = pd.to_datetime(df['Data'],
