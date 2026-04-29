import streamlit as st
import pandas as pd
from github import Github
import io
import os
from datetime import datetime

# 1. PREVENÇÃO CONTRA TRADUTOR E IDIOMA
st.markdown('<html lang="pt-br">', unsafe_allow_html=True)

# 2. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Logística Aura Apoena", layout="wide")

# 3. UI/UX DESIGN (CORES HARMONIZADAS)
st.markdown("""
    <style>
    /* Fundo Principal */
    .stApp { background-color: #FFFFFF; }
    
    /* Barra Lateral - Azul Marinho Aura */
    [data-testid="stSidebar"] {
        background-color: #002D5E !important;
    }
    
    /* Textos da Barra Lateral */
    [data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] p, [data-testid="stSidebar"] label {
        color: #FFFFFF !important;
    }

    /* Campos de Entrada - Fundo Branco e Texto PRETO (Contraste Máximo) */
    .stTextInput input, .stSelectbox div[data-baseweb="select"], .stDateInput input {
        background-color: #FFFFFF !important;
        border: 1.5px solid #002D5E !important;
        color: #000000 !important; /* Escrita em preto */
        border-radius: 5px !important;
    }
    
    /* Ajuste para o texto dentro do selectbox */
    div[data-baseweb="select"] > div {
        color: #000000 !important;
    }

    /* Botões - Azul Marinho com Texto Branco */
    div.stButton > button {
        background-color: #002D5E;
        color: white !important;
        border-radius: 5px;
        border: none;
        font-weight: bold;
        width: 100%;
    }
    
    div.stButton > button:hover {
        background-color: #E8E8E8 !important;
        color: #002D5E !important;
        border: 1px solid #002D5E !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 4. BACKEND (CONEXÃO GITHUB)
def carregar_dados():
    try:
        g = Github(st.secrets["GITHUB_TOKEN"])
        repo = g.get_repo("yaramaia122-lgtm/logistica-aura")
        contents = repo.get_contents("dados_logistica.csv")
        df = pd.read_csv(io.StringIO(contents.decoded_content.decode()))
        return df, contents.sha, repo
    except:
        return pd.DataFrame(columns=["Passageiro", "Motorista", "Data", "Trajeto"]), None, None

df, sha, repo = carregar_dados()

# 5. SIDEBAR / MENU
with st.sidebar:
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Tenta carregar a imagem do link RAW corrigido (sem espaços e parênteses no link interno)
    # DICA: Renomeie o arquivo no GitHub para logo.png para garantir 100% de sucesso
    logo_url = "https://raw.githubusercontent.com/yaramaia122-lgtm/logistica-aura/main/logo.png"
    
    # Fallback: Se ainda não renomeou, tenta o link antigo mas com tratamento
    try:
        st.image(logo_url, width=220)
    except:
        st.image("https://raw.githubusercontent.com/yaramaia122-lgtm/logistica-aura/main/Aura%20(Azul%20e%20Ocre)%20(1).png", width=220)
    
    st.markdown("---")
    menu = st.radio("Selecione:", ["📋 Agenda", "📝 Programar Viagem", "💰 Financeiro"])

# 6. TELAS
if menu == "📝 Programar Viagem":
    st.title("📝 Programar Nova Viagem")
    with st.form("form_viagem", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            passag = st.text_input("Passageiro").upper()
            motor = st.selectbox("Motorista", ["Ilson", "Antonio", "Outro"])
        with c2:
            data_v = st.date_input("Data", datetime.now())
            trajet = st.selectbox("Trajeto", ["P. Lacerda x Cuiabá", "Interno", "Outro"])
        
        if st.form_submit_button("Salvar Agendamento"):
            if passag and repo:
                nova_linha = pd.DataFrame([[passag, motor, data_v.strftime('%d/%m/%Y'), trajet]], columns=df.columns)
                df_final = pd.concat([df, nova_linha], ignore_index=True)
                csv_base = df_final.to_csv(index=False)
                if sha:
                    repo.update_file("dados_logistica.csv", "Update", csv_base, sha)
                else:
                    repo.create_file("dados_logistica.csv", "Init", csv_base)
                st.success("Viagem cadastrada!")
                st.rerun()

elif menu == "📋 Agenda":
    st.title("📋 Agenda de Logística")
    st.dataframe(df, use_container_width=True)

elif menu == "💰 Financeiro":
    st.title("💰 Edição de Dados")
    df_ed = st.data_editor(df, num_rows="dynamic", use_container_width=True)
    if st.button("Salvar Alterações no Banco"):
        if repo:
            csv_editado = df_ed.to_csv(index=False)
            repo.update_file("dados_logistica.csv", "Edit", csv_editado, sha)
            st.success("Dados atualizados!")
            st.rerun()
