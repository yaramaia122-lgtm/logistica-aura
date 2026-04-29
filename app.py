import streamlit as st
import pandas as pd
from github import Github
import io
from datetime import datetime

# Prevenção contra tradutor do Chrome
st.markdown('<html lang="pt-br">', unsafe_allow_html=True)

st.set_page_config(page_title="Aura Apoena - Logística", layout="wide")

# Estilização Aura Minerals
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    [data-testid="stSidebar"] { background-color: #002D5E; }
    [data-testid="stSidebar"] * { color: white !important; }
    .stTextInput input, .stSelectbox div[data-baseweb="select"], .stDateInput input {
        background-color: #E8E8E8 !important; border: 1px solid #002D5E !important; color: #002D5E !important;
    }
    div.stButton > button {
        background-color: #E8E8E8; color: #002D5E; border: 1px solid #002D5E;
        border-radius: 5px; width: 100%; font-weight: bold;
    }
    div.stButton > button:hover { background-color: #002D5E !important; color: white !important; }
    .logo-container { display: flex; justify-content: center; padding: 10px; }
    .logo-img { filter: drop-shadow(0px 4px 6px rgba(0,0,0,0.4)); width: 180px; }
    </style>
    """, unsafe_allow_html=True)

# Lógica de conexão resiliente
def conectar_github():
    try:
        token = st.secrets["GITHUB_TOKEN"]
        g = Github(token)
        return g.get_repo("yaramaia122-lgtm/logistica-aura")
    except Exception as e:
        st.error(f"Erro de conexão: {e}")
        return None

def carregar_dados():
    repo = conectar_github()
    if repo:
        try:
            contents = repo.get_contents("dados_logistica.csv")
            df = pd.read_csv(io.StringIO(contents.decoded_content.decode()))
            return df, contents.sha
        except:
            return pd.DataFrame(columns=["Passageiro", "Motorista", "Data", "Trajeto"]), None
    return pd.DataFrame(), None

def salvar_dados(df, sha=None):
    repo = conectar_github()
    if repo:
        csv_content = df.to_csv(index=False)
        try:
            if sha: repo.update_file("dados_logistica.csv", "Update", csv_content, sha)
            else: repo.create_file("dados_logistica.csv", "Novo", csv_content)
            return True
        except Exception as e:
            st.error(f"Erro ao salvar: {e}")
    return False

# Interface
df, file_sha = carregar_dados()

with st.sidebar:
    st.markdown('<div class="logo-container"><img src="https://raw.githubusercontent.com/yaramaia122-lgtm/logistica-aura/main/Aura%20(Azul%20e%20Ocre)%20(1).png" class="logo-img"></div>', unsafe_allow_html=True)
    st.markdown("---")
    menu = st.radio("MENU", ["📋 Agenda", "📝 Programar Viagem", "💰 Financeiro"])

if menu == "📝 Programar Viagem":
    st.header("📝 Programar Viagem")
    with st.form("f1", clear_on_submit=True):
        p = st.text_input("Passageiro").upper()
        m = st.selectbox("Motorista", ["Ilson", "Antonio", "Outro"])
        d = st.date_input("Data", datetime.now())
        t = st.selectbox("Trajeto", ["P. Lacerda x Cuiabá", "Interno", "Outro"])
        if st.form_submit_button("Agendar"):
            if p:
                novo = pd.DataFrame([[p, m, d.strftime('%Y-%m-%d'), t]], columns=df.columns)
                if salvar_dados(pd.concat([df, novo], ignore_index=True), file_sha):
                    st.success("Salvo com sucesso!"); st.rerun()

elif menu == "📋 Agenda":
    st.header("📋 Agenda")
    st.dataframe(df, use_container_width=True)

elif menu == "💰 Financeiro":
    st.header("💰 Financeiro")
    df_ed = st.data_editor(df, num_rows="dynamic", use_container_width=True)
    if st.button("Confirmar Alterações"):
        if salvar_dados(df_ed, file_sha):
            st.success("Planilha atualizada!"); st.rerun()
