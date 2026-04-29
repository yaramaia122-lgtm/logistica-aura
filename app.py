import streamlit as st
import pandas as pd
from github import Github
import io
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Aura Apoena - Logística", layout="wide")

# --- ESTILIZAÇÃO CUSTOMIZADA (CSS) ---
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
    .logo-img { filter: drop-shadow(0px 4px 6px rgba(0,0,0,0.5)); width: 180px; }
    </style>
    """, unsafe_allow_html=True)

# --- CONFIGURAÇÕES DO GITHUB (ATUALIZADO PARA SEU REPO) ---
try:
    TOKEN = st.secrets["GITHUB_TOKEN"]
    REPO_NAME = "yaramaia122-lgtm/logistica-aura" # Seu repositório real
    FILE_PATH = "dados_logistica.csv"
except Exception as e:
    st.error(f"Erro ao carregar Segredos: {e}")
    st.stop()

def carregar_dados():
    try:
        g = Github(TOKEN)
        repo = g.get_repo(REPO_NAME)
        contents = repo.get_contents(FILE_PATH)
        df = pd.read_csv(io.StringIO(contents.decoded_content.decode()))
        return df, contents.sha
    except Exception:
        # Se o arquivo não existir, cria estrutura básica
        return pd.DataFrame(columns=["Passageiro", "Motorista", "Data", "Trajeto"]), None

def salvar_dados(df, sha=None):
    try:
        g = Github(TOKEN)
        repo = g.get_repo(REPO_NAME)
        csv_content = df.to_csv(index=False)
        if sha:
            repo.update_file(FILE_PATH, "Update dados", csv_content, sha)
        else:
            repo.create_file(FILE_PATH, "Criação inicial", csv_content)
        return True
    except Exception as e:
        st.error(f"Erro ao salvar no GitHub: {e}")
        return False

# --- INTERFACE ---
df, file_sha = carregar_dados()

with st.sidebar:
    # Usei o link da logo que você enviou anteriormente, adaptado para raw
    st.markdown('<div class="logo-container"><img src="https://raw.githubusercontent.com/yaramaia122-lgtm/logistica-aura/main/Aura%20(Azul%20e%20Ocre)%20(1).png" class="logo-img"></div>', unsafe_allow_html=True)
    st.markdown("---")
    menu = st.radio("Navegação", ["📋 Agenda", "📝 Programar Viagem", "💰 Financeiro"])

if menu == "📝 Programar Viagem":
    st.subheader("Programar Viagem")
    with st.form("form_viagem"):
        col1, col2 = st.columns(2)
        with col1:
            passag = st.text_input("Passageiro").upper()
            motora = st.selectbox("Motorista", ["Ilson", "Antonio", "Outro"])
        with col2:
            data_v = st.date_input("Data", datetime.now())
            traje = st.selectbox("Trajeto", ["P. Lacerda x Cuiabá", "Interno", "Outro"])
        
        if st.form_submit_button("Confirmar Agendamento"):
            novo_dado = pd.DataFrame([[passag, motora, data_v, traje]], columns=df.columns)
            df_final = pd.concat([df, novo_dado], ignore_index=True)
            if salvar_dados(df_final, file_sha):
                st.success("Viagem salva!")
                st.rerun()

elif menu == "📋 Agenda":
    st.subheader("Agenda de Viagens")
    st.dataframe(df, use_container_width=True)

elif menu == "💰 Financeiro":
    st.subheader("Editar Registros")
    df_editado = st.data_editor(df, num_rows="dynamic",
