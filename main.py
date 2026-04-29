import streamlit as st
import pandas as pd
from github import Github
import io
from datetime import datetime

# 1. CONFIGURAÇÃO E TRAVAMENTO DE IDIOMA
st.set_page_config(page_title="Aura Apoena Logistics", layout="wide")

# 2. UI/UX - ESTRUTURA MAPEADA E CORES FIXAS (MARINHO, AZUL CLARO E PRETO)
st.markdown("""
<style>
    /* Fundo Principal Branco */
    .stApp { background-color: #FFFFFF !important; }
    
    /* Sidebar Azul Marinho */
    [data-testid="stSidebar"] { background-color: #002D5E !important; min-width: 280px; }
    
    /* Logo com Sombra */
    [data-testid="stSidebar"] [data-testid="stImage"] img {
        filter: drop-shadow(0px 10px 15px rgba(0,0,0,0.6));
    }

    /* TITULOS E DESCRIÇÕES: Azul Marinho Puro (Sem transparência) */
    h1, h2, h3, label, .stMarkdown p { 
        color: #002D5E !important; 
        font-weight: bold !important; 
        opacity: 1 !important;
    }
    
    /* CAMPOS DE PREENCHIMENTO: Azul Claro com Letras Pretas */
    .stTextInput input, .stSelectbox div[data-baseweb="select"], 
    .stDateInput input, .stNumberInput input {
        background-color: #F0F7FF !important; 
        border: 2px solid #002D5E !important;
        color: #000000 !important;
        border-radius: 8px !important;
        height: 45px !important;
    }

    /* Forçar cor preta no texto digitado para evitar fundo preto/letra branca */
    input { color: #000000 !important; -webkit-text-fill-color: #000000 !important; }
    div[data-baseweb="select"] span { color: #000000 !important; }

    /* BOTÕES: Azul Claro com Texto Marinho */
    div.stButton > button {
        background-color: #E1E8F0 !important;
        color: #002D5E !important;
        border: 2px solid #002D5E !important;
        font-weight: 800 !important;
        width: 100% !important;
        height: 50px !important;
    }
    
    /* Texto da Sidebar sempre Branco */
    [data-testid="stSidebar"] .stMarkdown p, [data-testid="stSidebar"] label { color: #FFFFFF !important; }
</style>
""", unsafe_allow_html=True)

# 3. BACKEND - CONEXÃO GITHUB
def carregar_dados():
    cols = ["Passageiro", "Motorista", "Data", "Trajeto", "Obs", "Hotel", "Combustivel", "Aereo", "Outros", "Total"]
    try:
        g = Github(st.secrets["GITHUB_TOKEN"])
        repo = g.get_repo("yaramaia122-lgtm/logistica-aura")
        contents = repo.get_contents("dados_logistica.csv")
        df = pd.read_csv(io.StringIO(contents.decoded_content.decode()))
        for c in cols:
            if c not in df.columns: df[c] = 0.0 if c in ["Hotel", "Combustivel", "Aereo", "Outros", "Total"] else ""
        return df, contents.sha, repo
    except:
        return pd.DataFrame(columns=cols), None, None

df, sha, repo = carregar_dados()

# 4. SIDEBAR
with st.sidebar:
    st.markdown("<br>", unsafe_allow_html=True)
    st.image("https://raw.githubusercontent.com/yaramaia122-lgtm/logistica-aura/main/logo.png", width=220)
    st.markdown("---")
    menu = st.radio("NAVEGACAO", ["Agenda", "Programar Viagem", "Financeiro"])

# 5. TELAS E MÓDULOS

if menu == "Agenda":
    st.title("📋 Agenda de Viagens")
    st.dataframe(df[["Passageiro", "Motorista", "Data", "Trajeto", "Obs"]], use_container_width=True)

elif menu == "Programar Viagem":
    st.title("📝 Programar Viagem")
    
    # Formulário com estrutura mapeada em colunas alinhadas
    with st.form("form_viagem", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            nome = st.text_input("Nome do Passageiro").upper()
            moto = st.selectbox("Motorista Designado", ["Ilson", "Antonio", "Outro"])
            v_h = st.number_input("Custo Hotel (R$)", min_value=0.0, format="%.2f")
            v_a = st.number_input("Custo Aéreo (R$)", min_value=0.0, format="%.2f")
