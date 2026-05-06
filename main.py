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

MESES_PT = {1:'jan', 2:'fev', 3:'mar', 4:'abr', 5:'mai', 6:'jun', 7:'jul', 8:'ago', 9:'set', 10:'out', 11:'nov', 12:'dez'}
DIAS_SEMANA_PT = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"]

# ==========================================================
# 1. TEMA E CSS (ESPECIFICIDADE TÉCNICA AVANÇADA)
# ==========================================================
def forcar_tema_claro():
    try:
        os.makedirs(".streamlit", exist_ok=True)
        arquivo = ".streamlit/config.toml"
        conteudo = "[theme]\nbase='light'\nprimaryColor='#002D5E'\n"
        if not os.path.exists(arquivo):
            with open(arquivo, "w") as f: f.write(conteudo)
    except: pass

st.set_page_config(page_title="Aura Apoena Logistics", layout="wide")
forcar_tema_claro()

st.markdown("""
<style>
    /* 1. RESET DE FUNDO DA APLICAÇÃO */
    .stApp { background-color: #FFFFFF !important; }
    [data-testid="stSidebar"] { background-color: #002D5E !important; }
    
    /* 2. TIPOGRAFIA GLOBAL */
    h1, h2, h3, label, .stMarkdown p { color: #002D5E !important; font-weight: 700 !important; }
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] label, [data-testid="stSidebar"] span { color: #FFFFFF !important; }

    /* 3. INPUTS E CAMPOS DE FORMULÁRIO */
    .stTextInput input, .stSelectbox div[data-baseweb="select"], .stDateInput input, .stNumberInput input { 
        background-color: #F0F7FF !important; 
        border: 2px solid #002D5E !important; 
        border-radius: 6px !important; 
        color: #002D5E !important; 
    }
    
    /* 4. ENGENHARIA DO BOTÃO (ESTADO NORMAL) */
    /* Selecionamos o botão e o parágrafo interno com prioridade máxima */
    div.stButton > button {
        background-color: #FFFFFF !important;
        border: 2px solid #002D5E !important;
        border-radius: 8px !important;
        width: 100% !important;
        height: 50px !important;
    }
    
    div.stButton > button p {
        color: #002D5E !important; /* AZUL MARINHO NO FUNDO BRANCO */
        font-weight: 900 !important;
        font-size: 16px !important;
        margin: 0px !important;
    }

    /* 5. ENGENHARIA DO BOTÃO (ESTADO HOVER/MOUSE) */
    div.stButton > button:hover {
        background-color: #002D5E !important;
        border: 2px solid #002D5E !important;
    }
    
    div.stButton > button:hover p {
        color: #FFFFFF !important; /* BRANCO NO FUNDO AZUL */
    }
    
    /* 6. CORREÇÃO ESPECÍFICA PARA TELA DE LOGIN (FUNDO ESCURO) */
    .login-container { 
        background-color: #002D5E; 
        padding: 30px; 
        border-radius: 15px;
    }
    
    /* Estilo Especial para a Tabela de Observações */
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
        
        try:
            cont_v = repo.get_contents("dados_logistica.csv")
            df_v = pd.read_csv(io.StringIO(cont_v.decoded_content.decode()))
