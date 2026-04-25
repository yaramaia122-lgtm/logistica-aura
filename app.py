import streamlit as st
import pandas as pd
from github import Github
import io
from datetime import datetime

# 1. VISUAL CORPORATIVO AURA (ESTILO BLINDADO)
st.set_page_config(page_title="Logística Aura Minerals", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF !important; }
    [data-testid="stSidebar"] { background-color: #002D5E !important; }
    [data-testid="stSidebar"] * { color: #FFFFFF !important; }
    h1, h2, h3, label { color: #002D5E !important; }
    
    /* Inputs Cinza Aura */
    div[data-baseweb="input"], div[data-baseweb="select"] {
        background-color: #E8E8E8 !important;
        border: 1px solid #002D5E !important;
    }
    
    /* Botões Aura */
    .stButton>button {
        background-color: #E8E8E8 !important;
        color: #002D5E !important;
        border: 2px solid #002D5E !important;
        font-weight: bold; width: 100%;
    }
    .stButton>button:hover { background-color: #002D5E !important; color: #FFFFFF !important; }
    
    .logo-aura { filter: drop-shadow(0px 4px 8px rgba(0,0,0,0.5)); display: block; margin: auto; }
    </style>
    """, unsafe_allow_html=True)

# 2. CONEXÃO COM O GITHUB (BANCO DE DADOS)
def conectar_github():
    try:
        # Pega a chave que você vai salvar no painel do Streamlit
        token = st.secrets["GITHUB_TOKEN"]
        g = Github(token)
        # AJUSTE AQUI: coloque seu 'usuario/repositorio'
        repo = g.get_user().get_repo("logistica-aura") 
        return repo
    except:
        st.error("Erro de conexão. Verifique o GITHUB_TOKEN nos Secrets.")
        return None

def carregar_dados_github(repo):
    file_path = "dados_logistica.csv"
    try:
        file_content = repo.get_contents(file_path)
        df = pd.read_csv(io.StringIO(file_content.decoded_content.decode('utf-8')))
        return df, file_content.sha
    except:
        # Se o arquivo não existir, cria um novo
        df_novo = pd.DataFrame(columns=["Data", "Motorista", "Passageiro", "Trajeto", "Valor"])
        return df_novo, None

def salvar_dados_github(repo, df, sha):
    file_path = "dados_logistica.csv"
    csv_string = df.to_csv(index=False)
    if sha:
        repo.update_file(file_path, "Update dados", csv_string, sha)
    else:
        repo.create_file(file_path, "Create dados", csv_string)

# 3. INTERFACE PRINCIPAL
repo = conectar_github()
if repo:
    df, sha = carregar_dados_github(repo)

    with st.sidebar:
        st.markdown('<div style="text-align: center;"><img src="https://gist.githubusercontent.com/user-attachments/assets/8e0f5228-40b9-4674-9f0f-6df3d57b280c" width="180" class="logo-aura"></div>', unsafe_allow_html=True)
        menu = st.radio("MENU", ["📋 Agenda", "📝 Programar", "💰 Financeiro"])

    if menu == "📝 Programar":
        st.header("📝 Programar Nova Viagem")
        with st.form("nova_viagem"):
            pax = st.text_input("Passageiro").upper()
            mot = st.selectbox("Motorista", ["Ilson", "Antonio", "Outro"])
            tra = st.selectbox("Trajeto", ["P. LACERDA X CUIABÁ", "INTERNO", "OUTRO"])
            if st.form_submit_button("✅ SALVAR NA NUVEM"):
                nova_linha = pd.DataFrame([{"Data": datetime.now().strftime('%d/%m/%Y'), "Motorista": mot, "Passageiro": pax, "Trajeto": tra, "Valor": 0}])
                df_final = pd.concat([df, nova_linha], ignore_index=True)
                salvar_dados_github(repo, df_final, sha)
                st.success("Dados salvos no GitHub!")
                st.rerun()

    elif menu == "📋 Agenda":
        st.header("📋 Agenda de Viagens")
        st.dataframe(df, use_container_width=True)

    elif menu == "💰 Financeiro":
        st.header("💰 Controle de Custos")
        df_editado = st.data_editor(df, use_container_width=True, num_rows="dynamic")
        if st.button("💾 ATUALIZAR TUDO"):
            salvar_dados_github(repo, df_editado, sha)
            st.success("Tabela financeira atualizada!")
