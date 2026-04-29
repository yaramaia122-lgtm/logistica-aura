import streamlit as st
import pandas as pd
from github import Github
import io
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Aura Apoena - Logística", layout="wide")

# --- ESTILIZAÇÃO CUSTOMIZADA (CSS) ---
st.markdown(f"""
    <style>
    /* Fundo principal */
    .stApp {{
        background-color: #FFFFFF;
    }}
    
    /* Barra lateral */
    [data-testid="stSidebar"] {{
        background-color: #002D5E;
    }}
    [data-testid="stSidebar"] * {{
        color: white !important;
    }}

    /* Inputs e bordas */
    .stTextInput input, .stSelectbox div[data-baseweb="select"], .stDateInput input {{
        background-color: #E8E8E8 !important;
        border: 1px solid #002D5E !important;
        color: #002D5E !important;
    }}

    /* Botões */
    div.stButton > button {{
        background-color: #E8E8E8;
        color: #002D5E;
        border: 1px solid #002D5E;
        border-radius: 5px;
        transition: all 0.3s ease;
    }}
    div.stButton > button:hover {{
        background-color: #002D5E !important;
        color: white !important;
    }}

    /* Logo com sombra */
    .logo-container {{
        display: flex;
        justify-content: center;
        padding: 10px;
    }}
    .logo-img {{
        filter: drop-shadow(0px 4px 6px rgba(0,0,0,0.5));
        width: 180px;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- INTEGRAÇÃO GITHUB ---
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
REPO_NAME = "SEU_USUARIO/SEU_REPOSITORIO" # <--- AJUSTE AQUI
FILE_PATH = "dados_logistica.csv"

def get_github_repo():
    g = Github(GITHUB_TOKEN)
    return g.get_repo(REPO_NAME)

def carregar_dados():
    try:
        repo = get_github_repo()
        contents = repo.get_contents(FILE_PATH)
        df = pd.read_csv(io.StringIO(contents.decoded_content.decode()))
        return df, contents.sha
    except:
        # Se o arquivo não existir, retorna um DF vazio
        return pd.DataFrame(columns=["Passageiro", "Motorista", "Data", "Trajeto"]), None

def salvar_dados(df, sha=None, mensagem="Update logística"):
    repo = get_github_repo()
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    if sha:
        repo.update_file(FILE_PATH, mensagem, csv_buffer.getvalue(), sha)
    else:
        repo.create_file(FILE_PATH, mensagem, csv_buffer.getvalue())

# --- SIDEBAR / MENU ---
with st.sidebar:
    st.markdown('<div class="logo-container"><img src="https://raw.githubusercontent.com/seu-repo/main/logo.png" class="logo-img"></div>', unsafe_allow_html=True)
    st.markdown("---")
    menu = st.radio("Navegação", ["📋 Agenda", "📝 Programar Viagem", "💰 Financeiro"])

df, file_sha = carregar_dados()

# --- LOGICA DAS TELAS ---

if menu == "📝 Programar Viagem":
    st.header("📝 Programar Nova Viagem")
    with st.form("form_viagem", clear_on_submit=True):
        passageiro = st.text_input("Passageiro").upper()
        motorista = st.selectbox("Motorista", ["Ilson", "Antonio", "Outro"])
        data = st.date_input("Data", datetime.now())
        trajeto = st.selectbox("Trajeto", ["P. Lacerda x Cuiabá", "Interno", "Outro"])
        
        submit = st.form_submit_button("Agendar Viagem")
        
        if submit:
            nova_linha = pd.DataFrame([{
                "Passageiro": passageiro,
                "Motorista": motorista,
                "Data": data.strftime('%Y-%m-%d'),
                "Trajeto": trajeto
            }])
            df_final = pd.concat([df, nova_linha], ignore_index=True)
            salvar_dados(df_final, file_sha)
            st.success("Viagem programada com sucesso!")
            st.rerun()

elif menu == "📋 Agenda":
    st.header("📋 Agenda de Viagens")
    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Nenhuma viagem agendada.")

elif menu == "💰 Financeiro":
    st.header("💰 Controle Financeiro e Edição")
    st.warning("Edite as células abaixo e clique em 'Salvar Alterações'.")
    
    # Editor de dados para deleção e modificação
    df_editado = st.data_editor(df, num_rows="dynamic", use_container_width=True)
    
    if st.button("Salvar Alterações"):
        salvar_dados(df_editado, file_sha, "Alteração via aba Financeiro")
        st.success("Dados atualizados no GitHub!")
        st.rerun()
