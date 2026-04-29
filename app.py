import streamlit as st
import pandas as pd
from github import Github
import io
from datetime import datetime

# Previne erro de tradução automática do navegador
st.markdown('<html lang="pt-br">', unsafe_allow_html=True)

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Aura Apoena - Logística", layout="wide")

# --- IDENTIDADE VISUAL (CSS) ---
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    [data-testid="stSidebar"] { background-color: #002D5E; }
    [data-testid="stSidebar"] * { color: white !important; }
    .stTextInput input, .stSelectbox div[data-baseweb="select"], .stDateInput input {
        background-color: #E8E8E8 !important;
        border: 1px solid #002D5E !important;
        color: #002D5E !important;
    }
    div.stButton > button {
        background-color: #E8E8E8;
        color: #002D5E;
        border: 1px solid #002D5E;
        border-radius: 5px;
        transition: all 0.3s ease;
        width: 100%;
    }
    div.stButton > button:hover {
        background-color: #002D5E !important;
        color: white !important;
    }
    .logo-container { display: flex; justify-content: center; padding: 10px; }
    .logo-img { filter: drop-shadow(0px 4px 6px rgba(0,0,0,0.4)); width: 180px; }
    </style>
    """, unsafe_allow_html=True)

# --- CONFIGURAÇÕES GITHUB ---
try:
    TOKEN = st.secrets["GITHUB_TOKEN"]
    REPO_NAME = "yaramaia122-lgtm/logistica-aura"
    FILE_PATH = "dados_logistica.csv"
except:
    st.error("ERRO: GITHUB_TOKEN não configurado nos Secrets do Streamlit.")
    st.stop()

def carregar_dados():
    try:
        g = Github(TOKEN)
        repo = g.get_repo(REPO_NAME)
        contents = repo.get_contents(FILE_PATH)
        df = pd.read_csv(io.StringIO(contents.decoded_content.decode()))
        return df, contents.sha
    except:
        return pd.DataFrame(columns=["Passageiro", "Motorista", "Data", "Trajeto"]), None

def salvar_dados(df, sha=None):
    try:
        g = Github(TOKEN)
        repo = g.get_repo(REPO_NAME)
        csv_content = df.to_csv(index=False)
        if sha:
            repo.update_file(FILE_PATH, "Update Logística", csv_content, sha)
        else:
            repo.create_file(FILE_PATH, "Novo Arquivo", csv_content)
        return True
    except Exception as e:
        st.error(f"Erro ao salvar: {e}")
        return False

# --- APP ---
df, file_sha = carregar_dados()

with st.sidebar:
    # Logo usando o arquivo do seu repositório
    st.markdown('<div class="logo-container"><img src="https://raw.githubusercontent.com/yaramaia122-lgtm/logistica-aura/main/Aura%20(Azul%20e%20Ocre)%20(1).png" class="logo-img"></div>', unsafe_allow_html=True)
    st.markdown("---")
    menu = st.radio("NAVEGAÇÃO", ["📋 Agenda", "📝 Programar Viagem", "💰 Financeiro"])

if menu == "📝 Programar Viagem":
    st.subheader("📝 Programar Nova Viagem")
    with st.form("form_viagem", clear_on_submit=True):
        p = st.text_input("Passageiro (Nome Completo)").upper()
        m = st.selectbox("Motorista", ["Ilson", "Antonio", "Outro"])
        d = st.date_input("Data", datetime.now())
        t = st.selectbox("Trajeto", ["P. Lacerda x Cuiabá", "Interno", "Outro"])
        if st.form_submit_button("Confirmar Agendamento"):
            if p:
                novo = pd.DataFrame([[p, m, d.strftime('%Y-%m-%d'), t]], columns=df.columns)
                df_final = pd.concat([df, novo], ignore_index=True)
                if salvar_dados(df_final, file_sha):
                    st.success("Viagem salva!")
                    st.rerun()
            else:
                st.warning("Preencha o nome do passageiro.")

elif menu == "📋 Agenda":
    st.subheader("📋 Agenda de Viagens")
    st.dataframe(df, use_container_width=True)

elif menu == "💰 Financeiro":
    st.subheader("💰 Edição e Financeiro")
    df_ed = st.data_editor(df, num_rows="dynamic", use_container_width=True)
    if st.button("Salvar Alterações"):
        if salvar_dados(df_ed, file_sha):
            st.success("Planilha atualizada!")
            st.rerun()
