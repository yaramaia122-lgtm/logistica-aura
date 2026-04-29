import streamlit as st
import pandas as pd
from github import Github
import io
import os
from datetime import datetime

# Prevenção contra tradutor do navegador
st.markdown('<html lang="pt-br">', unsafe_allow_html=True)

st.set_page_config(page_title="Logística Aura Apoena", layout="wide")

# --- ESTILO E CORES HARMONIZADAS ---
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    [data-testid="stSidebar"] { background-color: #002D5E !important; }
    [data-testid="stSidebar"] * { color: white !important; }
    
    /* Caixas de Texto - Fundo branco, borda cinza e letra PRETA para leitura */
    .stTextInput input, .stSelectbox div[data-baseweb="select"], .stDateInput input {
        background-color: #FFFFFF !important;
        border: 1px solid #002D5E !important;
        color: #000000 !important;
        border-radius: 5px !important;
    }
    
    /* Botão Salvar - Azul com letra branca */
    div.stButton > button {
        background-color: #002D5E;
        color: white;
        border-radius: 5px;
        width: 100%;
        font-weight: bold;
    }
    div.stButton > button:hover {
        background-color: #E8E8E8 !important;
        color: #002D5E !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- CONEXÃO GITHUB ---
def carregar_banco():
    try:
        g = Github(st.secrets["GITHUB_TOKEN"])
        repo = g.get_repo("yaramaia122-lgtm/logistica-aura")
        contents = repo.get_contents("dados_logistica.csv")
        df = pd.read_csv(io.StringIO(contents.decoded_content.decode()))
        return df, contents.sha, repo
    except:
        return pd.DataFrame(columns=["Passageiro", "Motorista", "Data", "Trajeto"]), None, None

df, sha, repo = carregar_banco()

# --- BARRA LATERAL ---
with st.sidebar:
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Tenta carregar a imagem localmente (se estiver na mesma pasta do GitHub)
    if os.path.exists("logo.png"):
        st.image("logo.png", width=220)
    else:
        # Link reserva caso você ainda não tenha renomeado no GitHub
        st.image("https://raw.githubusercontent.com/yaramaia122-lgtm/logistica-aura/main/Aura%20(Azul%20e%20Ocre)%20(1).png", width=220)
    
    st.markdown("---")
    menu = st.radio("Selecione:", ["📋 Agenda", "📝 Programar Viagem", "💰 Financeiro"])

# --- TELAS ---
if menu == "📝 Programar Viagem":
    st.header("📝 Programar Nova Viagem")
    with st.form("viagem"):
        col1, col2 = st.columns(2)
        with col1:
            p = st.text_input("Passageiro").upper()
            m = st.selectbox("Motorista", ["Ilson", "Antonio", "Outro"])
        with col2:
            d = st.date_input("Data", datetime.now())
            t = st.selectbox("Trajeto", ["P. Lacerda x Cuiabá", "Interno", "Outro"])
        
        if st.form_submit_button("Confirmar Agendamento"):
            if p and repo:
                novo = pd.DataFrame([[p, m, d.strftime('%d/%m/%Y'), t]], columns=df.columns)
                df_f = pd.concat([df, novo], ignore_index=True)
                csv = df_f.to_csv(index=False)
                if sha: repo.update_file("dados_logistica.csv", "viagem", csv, sha)
                else: repo.create_file("dados_logistica.csv", "init", csv)
                st.success("Salvo!"); st.rerun()

elif menu == "📋 Agenda":
    st.header("📋 Agenda de Viagens")
    st.dataframe(df, width=1200)

elif menu == "💰 Financeiro":
    st.header("💰 Edição de Dados")
    ed = st.data_editor(df, num_rows="dynamic", width=1200)
    if st.button("Salvar Alterações"):
        if repo:
            csv = ed.to_csv(index=False)
            repo.update_file("dados_logistica.csv", "edit", csv, sha)
            st.success("Banco de dados atualizado!"); st.rerun()
