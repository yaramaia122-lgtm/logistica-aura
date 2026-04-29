import streamlit as st

# Isso ajuda a evitar que o tradutor automático quebre o app
st.markdown('<html lang="pt-br">', unsafe_allow_html=True)

# O restante do seu código vem abaixo...

import streamlit as st
import pandas as pd
from github import Github
import io
from datetime import datetime

# --- PREVENÇÃO CONTRA TRADUTOR AUTOMÁTICO ---
st.markdown('<html lang="pt-br">', unsafe_allow_html=True)

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Aura Apoena - Logística", layout="wide")

# --- ESTILIZAÇÃO CUSTOMIZADA (CSS) ---
st.markdown("""
    <style>
    /* Fundo e Barra Lateral */
    .stApp { background-color: #FFFFFF; }
    [data-testid="stSidebar"] { background-color: #002D5E; }
    [data-testid="stSidebar"] * { color: white !important; }
    
    /* Inputs */
    .stTextInput input, .stSelectbox div[data-baseweb="select"], .stDateInput input {
        background-color: #E8E8E8 !important;
        border: 1px solid #002D5E !important;
        color: #002D5E !important;
    }

    /* Botões Customizados */
    div.stButton > button {
        background-color: #E8E8E8;
        color: #002D5E;
        border: 1px solid #002D5E;
        border-radius: 5px;
        transition: all 0.3s ease;
        width: 100%;
        font-weight: bold;
    }
    div.stButton > button:hover {
        background-color: #002D5E !important;
        color: white !important;
    }

    /* Logo com Sombra */
    .logo-container { display: flex; justify-content: center; padding: 10px; }
    .logo-img { filter: drop-shadow(0px 4px 6px rgba(0,0,0,0.5)); width: 180px; }
    </style>
    """, unsafe_allow_html=True)

# --- CONFIGURAÇÕES DE ACESSO ---
try:
    TOKEN = st.secrets["GITHUB_TOKEN"]
    REPO_NAME = "yaramaia122-lgtm/logistica-aura"
    FILE_PATH = "dados_logistica.csv"
except Exception as e:
    st.error("Erro nos Segredos: Verifique se o GITHUB_TOKEN está configurado no Streamlit Cloud.")
    st.stop()

# --- FUNÇÕES DE DADOS ---
def carregar_dados():
    try:
        g = Github(TOKEN)
        repo = g.get_repo(REPO_NAME)
        contents = repo.get_contents(FILE_PATH)
        df = pd.read_csv(io.StringIO(contents.decoded_content.decode()))
        return df, contents.sha
    except Exception:
        # Retorna estrutura vazia se o arquivo não existir
        return pd.DataFrame(columns=["Passageiro", "Motorista", "Data", "Trajeto"]), None

def salvar_dados(df, sha=None):
    try:
        g = Github(TOKEN)
        repo = g.get_repo(REPO_NAME)
        csv_content = df.to_csv(index=False)
        if sha:
            repo.update_file(FILE_PATH, "Update via App Logística", csv_content, sha)
        else:
            repo.create_file(FILE_PATH, "Criação inicial de dados", csv_content)
        return True
    except Exception as e:
        st.error(f"Erro ao salvar: {e}")
        return False

# --- INTERFACE PRINCIPAL ---
df, file_sha = carregar_dados()

with st.sidebar:
    # Logo centralizada
    st.markdown('<div class="logo-container"><img src="https://raw.githubusercontent.com/yaramaia122-lgtm/logistica-aura/main/Aura%20(Azul%20e%20Ocre)%20(1).png" class="logo-img"></div>', unsafe_allow_html=True)
    st.markdown("---")
    menu = st.radio("MENU PRINCIPAL", ["📋 Agenda", "📝 Programar Viagem", "💰 Financeiro"])

if menu == "📝 Programar Viagem":
    st.title("📝 Programar Viagem")
    with st.form("form_viagem"):
        col1, col2 = st.columns(2)
        with col1:
            passag = st.text_input("Nome do Passageiro").upper()
            motora = st.selectbox("Motorista Responsável", ["Ilson", "Antonio", "Outro"])
        with col2:
            data_v = st.date_input("Data da Viagem", datetime.now())
            traje = st.selectbox("Trajeto", ["P. Lacerda x Cuiabá", "Interno", "Outro"])
        
        if st.form_submit_button("Confirmar Agendamento"):
            if passag:
                novo_registro = pd.DataFrame([[passag, motora, data_v, traje]], columns=df.columns)
                df_final = pd.concat([df, novo_registro], ignore_index=True)
                if salvar_dados(df_final, file_sha):
                    st.success("Viagem registrada com sucesso!")
                    st.rerun()
            else:
                st.warning("Por favor, digite o nome do passageiro.")

elif menu == "📋 Agenda":
    st.title("📋 Agenda de Logística")
    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Nenhum registro encontrado.")

elif menu == "💰 Financeiro":
    st.title("💰 Controle e Edição")
    st.write("Edite os dados diretamente na tabela abaixo e clique em salvar.")
    df_editado = st.data_editor(df, num_rows="dynamic", use_container_width=True)
    
    if st.button("Salvar Todas as Alterações"):
        if salvar_dados(df_editado, file_sha):
            st.success("Planilha atualizada no repositório!")
            st.rerun()
