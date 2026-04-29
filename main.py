import streamlit as st
import pandas as pd
from github import Github
import io
import os
from datetime import datetime

# 1. CONFIGURACAO DE AMBIENTE
st.set_page_config(page_title="Aura Apoena Logistics", layout="wide")
st.markdown('<html lang="pt-br">', unsafe_allow_html=True)

# 2. UI/UX - DESIGNER (ESTILO BLINDADO CONTRA ERROS DE SINTAXE)
# Removido emojis e acentos do CSS para evitar o erro de 'unterminated string'
st.markdown("""
<style>
    .stApp {background-color: #FFFFFF;}
    [data-testid="stSidebar"] {background-color: #002D5E !important; min-width: 280px;}
    
    /* Efeito de Sombra na Logo conforme solicitado */
    [data-testid="stSidebar"] [data-testid="stImage"] img {
        filter: drop-shadow(0px 10px 15px rgba(0,0,0,0.7));
    }

    /* Inputs: Azul Claro com Letras Pretas (Sustentado) */
    .stTextInput input, .stSelectbox div[data-baseweb="select"], 
    .stDateInput input, .stNumberInput input {
        background-color: #F0F7FF !important; 
        border: 2px solid #002D5E !important;
        color: #000000 !important;
        border-radius: 8px !important;
    }
    
    input, div[data-baseweb="select"] span {color: #000000 !important; font-weight: 500 !important;}

    /* Labels e Titulos */
    label, .stMarkdown p {color: #002D5E !important; font-weight: bold !important;}
    h1, h2, h3 {color: #002D5E !important;}

    /* Botoes: Azul Claro com Texto Marinho */
    div.stButton > button {
        background-color: #E1E8F0 !important;
        color: #002D5E !important;
        border: 2px solid #002D5E !important;
        font-weight: 700 !important;
        height: 50px !important;
        width: 100% !important;
    }
    
    /* Texto da Sidebar em Branco */
    [data-testid="stSidebar"] .stMarkdown p, [data-testid="stSidebar"] label {
        color: #FFFFFF !important;
    }
</style>
""", unsafe_allow_html=True)

# 3. BACKEND - CONEXAO COM GITHUB (ESTRUTURA ORIGINAL MANTIDA)
def carregar_dados():
    # Colunas detalhadas conforme sua necessidade de registrar hotel, aereo, etc.
    cols = ["Passageiro", "Motorista", "Data", "Trajeto", "Obs Itinerario", "Hotel", "Combustivel", "Aereo", "Outros", "Total"]
    try:
        g = Github(st.secrets["GITHUB_TOKEN"])
        repo = g.get_repo("yaramaia122-lgtm/logistica-aura")
        contents = repo.get_contents("dados_logistica.csv")
        df = pd.read_csv(io.StringIO(contents.decoded_content.decode()))
        # Garante que as colunas existam para nao dar erro no registro
        for c in cols:
            if c not in df.columns:
                df[c] = 0.0 if c in ["Hotel", "Combustivel", "Aereo", "Outros", "Total"] else ""
        return df, contents.sha, repo
    except:
        return pd.DataFrame(columns=cols), None, None

df, sha, repo = carregar_dados()

# 4. SIDEBAR - NAVEGACAO
with st.sidebar:
    st.markdown("<br>", unsafe_allow_html=True)
    # Logo nomeada como logo.png no seu repositorio
    logo = "https://raw.githubusercontent.com/yaramaia122-lgtm/logistica-aura/main/logo.png"
    st.image(logo, width=220)
    st.markdown("---")
    menu = st.radio("NAVEGACAO", ["Agenda", "Programar Viagem", "Financeiro"])

# 5. MODULOS DO SISTEMA

if menu == "Agenda":
    st.title("Agenda de Viagens")
    if not df.empty:
        # Exibe apenas logistica na agenda
        st.dataframe(df[["Passageiro", "Motorista", "Data", "Trajeto", "Obs Itinerario"]], use_container_width=True)
    else:
        st.info("Nenhum registro encontrado.")

elif menu == "Programar Viagem":
    st.title("Programar Nova Viagem")
    with st.form("form_registro", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            pax = st.text_input("Nome do Passageiro").upper()
            mot = st.selectbox("Motorista", ["Ilson",
