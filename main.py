import streamlit as st
import pandas as pd
from github import Github
import io
from datetime import datetime

# 1. PREVENÇÃO CONTRA TRADUTOR E IDIOMA
st.markdown('<html lang="pt-br">', unsafe_allow_html=True)

# 2. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Logística Aura Apoena", layout="wide")

# 3. UI/UX DESIGNER (ESTILIZAÇÃO DAS CORES)
st.markdown("""
    <style>
    /* Fundo Principal */
    .stApp { background-color: #FDFDFD; }
    
    /* Barra Lateral - Azul Marinho Aura */
    [data-testid="stSidebar"] {
        background-color: #002D5E !important;
        min-width: 300px;
    }
    
    /* Ajuste de cor dos textos na Barra Lateral */
    [data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] p, [data-testid="stSidebar"] label {
        color: #FFFFFF !important;
        font-weight: 500;
    }

    /* Estilização das Caixas de Texto (Fundo Branco e Escrita Preta) */
    .stTextInput input, .stSelectbox div[data-baseweb="select"], .stDateInput input {
        background-color: #FFFFFF !important;
        border: 2px solid #002D5E !important; /* Borda Azul Aura para combinar */
        color: #000000 !important; /* TEXTO EM PRETO PARA VER O QUE ESCREVE */
        border-radius: 6px !important;
        height: 45px !important;
    }
    
    /* Garante que o texto dentro do menu de seleção também fique preto */
    div[data-baseweb="select"] > div {
        color: #000000 !important;
    }

    /* Títulos e Cabeçalhos */
    h1, h2, h3 { 
        color: #002D5E !important; 
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    /* Botão Salvar - Estilo Profissional */
    div.stButton > button {
        background-color: #002D5E;
        color: #FFFFFF;
        border: none;
        border-radius: 6px;
        padding: 0.7rem 1.5rem;
        font-size: 16px;
        font-weight: bold;
        width: 100%;
    }
    
    div.stButton > button:hover {
        background-color: #E8E8E8 !important;
        color: #002D5E !important;
        border: 1px solid #002D5E !important;
    }

    /* Tabela de Dados */
    [data-testid="stDataFrame"] {
        border: 1px solid #E0E0E0;
        border-radius: 8px;
    }
    </style>
    """, unsafe_allow_html=True)

# 4. BACKEND (CONEXÃO GITHUB)
def carregar_sistema():
    try:
        g = Github(st.secrets["GITHUB_TOKEN"])
        repo = g.get_repo("yaramaia122-lgtm/logistica-aura")
        contents = repo.get_contents("dados_logistica.csv")
        df = pd.read_csv(io.StringIO(contents.decoded_content.decode()))
        return df, contents.sha, repo
    except:
        return pd.DataFrame(columns=["Passageiro", "Motorista", "Data", "Trajeto"]), None, None

df, sha, repo = carregar_sistema()

# 5. SIDEBAR / MENU
with st.sidebar:
    st.markdown("<br>", unsafe_allow_html=True)
    
    # URL DA LOGO - Ajustada para o formato raw correto do GitHub
    logo_path = "https://raw.githubusercontent.com/yaramaia122-lgtm/logistica-aura/main/Aura%20(Azul%20e%20Ocre)%20(1).png"
    
    # Tentativa de carregar a logo (width ajustado para visibilidade)
    st.image(logo_path, width=240)
    
    st.markdown("---")
    menu = st.radio("Navegação", ["📋 Agenda de Viagens", "📝 Programar Nova Viagem", "💰 Financeiro e Edição"])

# 6. TELAS
if menu == "📝 Programar Nova Viagem":
    st.title("📝 Programar Nova Viagem")
    with st.form("form_logistica"):
        c1, c2 = st.columns(2)
        with c1:
            nome = st.text_input("Passageiro (Nome Completo)").upper()
            motorista = st.selectbox("Motorista", ["Ilson", "Antonio", "Outro"])
        with c2:
            data = st.date_input("Data da Viagem", datetime.now())
            trajeto = st.selectbox("Trajeto", ["P. Lacerda x Cuiabá", "Interno", "Outro"])
        
        if st.form_submit_button("Confirmar Agendamento"):
            if nome and repo:
                nova_viagem = pd.DataFrame([[nome, motorista, data.strftime('%d/%m/%Y'), trajeto]], columns=df.columns)
                df_atualizado = pd.concat([df
