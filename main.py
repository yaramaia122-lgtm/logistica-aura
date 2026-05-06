import streamlit as st
import pandas as pd
from github import Github, Auth
import io
import os
from datetime import datetime, timedelta

# ==========================================================
# 0. INICIALIZAÇÃO DE SESSÃO E SEGURANÇA
# ==========================================================
if 'logado' not in st.session_state:
    st.session_state['logado'] = False
if 'usuario_atual' not in st.session_state:
    st.session_state['usuario_atual'] = ""
if 'perfil' not in st.session_state:
    st.session_state['perfil'] = ""
if 'precisa_trocar_senha' not in st.session_state:
    st.session_state['precisa_trocar_senha'] = False
if 'usuario_troca' not in st.session_state:
    st.session_state['usuario_troca'] = ""

DIAS_SEMANA_PT = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"]
MESES_PT = {1:'jan', 2:'fev', 3:'mar', 4:'abr', 5:'mai', 6:'jun', 7:'jul', 8:'ago', 9:'set', 10:'out', 11:'nov', 12:'dez'}

# ==========================================================
# 1. TEMA E CSS (VISIBILIDADE MÁXIMA DOS BOTÕES)
# ==========================================================
def forcar_tema_claro():
    try:
        os.makedirs(".streamlit", exist_ok=True)
        arquivo = ".streamlit/config.toml"
        conteudo = "[theme]\nbase='light'\nprimaryColor='#002D5E'\n"
        if not os.path.exists(arquivo):
            with open(arquivo, "w") as f: f.write(conteudo)
    except:
        pass

st.set_page_config(page_title="Aura Apoena Logistics", layout="wide")
forcar_tema_claro()

st.markdown("""
<style>
    /* Fundo Principal */
    .stApp { background-color: #FFFFFF !important; }
    [data-testid="stSidebar"] { background-color: #002D5E !important; }
    
    /* Textos em Azul Marinho */
    h1, h2, h3, label, .stMarkdown p { color: #002D5E !important; font-weight: 700 !important; }
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] label, [data-testid="stSidebar"] span { color: #FFFFFF !important; }

    /* --- ENGENHARIA DOS BOTÕES (CORREÇÃO DE VISIBILIDADE) --- */
    div.stButton > button {
        background-color: #FFFFFF !important;
        border: 2px solid #002D5E !important;
        border-radius: 8px !important;
        width: 100% !important;
        height: 50px !important;
        transition: 0.3s;
    }
    
    /* Força a cor do texto para Azul Marinho mesmo em temas escuros */
    div.stButton > button p {
        color: #002D5E !important;
        -webkit-text-fill-color: #002D5E !important;
        font-weight: 900 !important;
        font-size: 16px !important;
    }

    /* Efeito de Inversão no Mouse */
    div.stButton > button:hover {
        background-color: #002D5E !important;
    }
    div.stButton > button:hover p {
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
    }
    
    /* Estilo das Inputs */
    .stTextInput input, .stSelectbox div[data-baseweb="select"], .stDateInput input { 
        background-color: #F0F7FF !important; border: 2px solid #002D5E !important; color: #002D5E !important; 
    }

    .obs-header { background-color: #E75945 !important; color: white !important; text-align: center !important; padding: 10px !important; font-weight: bold !important; border-radius: 8px 8px 0px 0px; margin-bottom: -15px; }
</style>
""", unsafe_allow_html=True)

# ==========================================================
# 2. MOTOR DE BANCO DE DADOS
# ==========================================================
@st.cache_data(ttl=5)
def carregar_bancos():
    cols_v = ["Passageiro", "Motorista", "Data", "Semana", "Hora_Saida", "Trajeto", "Voo_Cia_Num", "Hora_Voo", "Data_Voo", "Local_Hotel", "Centro de Custo", "Status", "Hotel_Valor", "Combustivel_Valor", "Aereo_Valor", "Outros_Valor", "Total", "Usuario_Criador"]
    cols_u = ["Usuario", "Senha", "Perfil", "Status", "Primeiro_Acesso"]
    try:
        token = st.secrets["GITHUB_TOKEN"]
        auth = Auth.Token(token)
        g = Github(auth=auth)
        repo = g.get_repo("yaramaia122-lgtm/logistica-aura")
        
        # Viagens
        try:
            cont_v = repo.get_contents("dados_logistica.csv")
            df_v = pd.read_csv(io.StringIO(cont_v.decoded_content.decode()))
            sha_v = cont_v.sha
            for c in cols_v:
                if c not in df_v.columns: df_v[c] = 0.0 if "_Valor" in c or c == "Total" else ""
        except:
            df_v = pd.DataFrame(columns=cols_v); sha_v = None

        # Usuários
        try:
            cont_u = repo.get_contents("usuarios.csv")
            df_u = pd.read_csv(io.StringIO(cont_u.decoded_content.decode()))
            sha_u = cont_u.sha
        except:
            df_u = pd.DataFrame([["yara.chaves", "aura123", "Administrador", "Ativo", "Sim"]], columns=cols_u)
            repo.create_file("usuarios.csv", "Init", df_u.to_csv(index=False))
            sha_u = repo.get_contents("usuarios.csv").sha

        # Observações
        try:
            cont_o = repo.get_contents("observacoes.csv")
            df_o = pd.read_csv(io.StringIO(cont_o.decoded_content.decode()))
            sha_o = cont_o.sha
        except:
            df_o = pd.DataFrame(columns=["Data", "Observacao"]); sha_o = None

        return df_v, sha_v, df_u, sha_u, df_o, sha_o, repo
    except:
        return pd.DataFrame(),
