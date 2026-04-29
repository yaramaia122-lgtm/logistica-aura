import streamlit as st
import pandas as pd
from github import Github
import io
from datetime import datetime

# 1. PREVENÇÃO CONTRA TRADUTOR E IDIOMA
st.markdown('<html lang="pt-br">', unsafe_allow_html=True)

# 2. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Aura Apoena Logistics", layout="wide")

# 3. UI/UX PREMIUM DESIGN
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    [data-testid="stSidebar"] {
        background-color: #002D5E !important;
        min-width: 280px;
    }
    [data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] p, [data-testid="stSidebar"] label {
        color: #FFFFFF !important;
    }
    .stTextInput input, .stSelectbox div[data-baseweb="select"], .stDateInput input {
        background-color: #F0F7FF !important; 
        border: 1px solid #D1D9E6 !important;
        color: #002D5E !important;
        border-radius: 8px !important;
        height: 45px !important;
    }
    div.stButton > button {
        background-color: #EBF2FA;
        color: #002D5E !important;
        border: 1px solid #002D5E;
        border-radius: 8px;
        font-weight: 700;
        width: 100%;
        transition: all 0.3s;
    }
    div.stButton > button:hover {
        background-color: #002D5E !important;
        color: #FFFFFF !important;
    }
    [data-testid="stDataFrame"], [data-testid="stTable"], .stDataEditor {
        background-color: #FFFFFF !important;
        border-radius: 10px !important;
        padding: 5px;
    }
    div[data-testid="stDataFrame"] div[data-testid="stTable"] {
        color: #1A1A1A !important;
    }
    h1, h2, h3 { color: #002D5E !important; }
    </style>
    """, unsafe_allow_html=True)

# 4. BACKEND (CONEXÃO GITHUB)
def carregar_sistema():
    try:
        g = Github(st.secrets["GITHUB_TOKEN"])
        repo = g.get_repo("yaramaia122-lgtm/logistica-aura")
        contents = repo.get_contents("dados_logistica.csv")
        df = pd.read_csv(io.StringIO(contents.decoded_content.decode()))
        return df, contents.sha, repo
    except:
        return pd.DataFrame(columns=["Passageiro", "Motorista", "Data", "Trajeto", "Valor (R$)"]), None, None

df, sha, repo = carregar_sistema()

# 5. SIDEBAR / MENU
with st.sidebar:
    st.markdown("<br>", unsafe_allow_html=True)
    try:
        st.image("logo.png", width=240)
    except:
        st.image("https://raw.githubusercontent.com/yaramaia122-lgtm/logistica-aura/main/Aura%20(Azul%20e%20Ocre)%20(1).png", width=240)
    
    st.markdown("<br>", unsafe_allow_html=True)
    menu = st.radio("NAVEGAÇÃO:", ["📋 Agenda de Viagens", "📝 Programar Viagem", "💰 Financeiro"])

# 6. TELAS
if menu == "📝 Programar Viagem":
    st.title("📝 Programar Viagem")
    with st.form("form_v", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            nome = st.text_input("Nome do Passageiro").upper()
            motorista = st.selectbox("Motorista", ["Ilson", "Antonio", "Outro"])
        with c2:
            data = st.date_input("Data", datetime.now())
            trajeto = st.selectbox("Trajeto", ["P. Lacerda x Cuiabá", "Interno", "Outro"])
        
        valor = st.number_input("Valor da Viagem (R$)", min_value=0.0, step=10.0)
        
        if st.form_submit_button("SALVAR REGISTRO"):
            if nome and repo:
                nova_viagem = pd.DataFrame([[nome, motorista, data.strftime('%d/%m/%Y'), trajeto, valor]], columns=df.columns)
                df_f = pd.concat([df, nova_viagem], ignore_index=True)
                csv_data = df_f.to_csv(index=False)
                if sha:
                    repo.update_file("dados_logistica.csv", "Reg", csv_data, sha)
                else:
                    repo.create_file("dados_logistica.csv", "Init", csv_data)
                st.success(f"Viagem para {nome} salva!")
                st.rerun()

elif menu == "📋 Agenda de Viagens":
    st.title("📋 Agenda de Viagens")
    st.dataframe(df, use_container_width=True)

elif menu == "💰 Financeiro":
    st.title("💰 Controle Financeiro")
    st.write("Ajuste valores, custos ou remova registros nesta planilha:")
    
    # Adicionei a coluna de Valor na criação do DF caso ela não exista
    if "Valor (R$)" not in df.columns:
        df["Valor (R$)"] = 0.0

    df_editado = st.data_editor(df, num_rows="dynamic", use_container_width=True)
    
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("CONFIRMAR ALTERAÇÕES"):
            if repo:
                csv_editado = df_editado.to_csv(index=False)
                repo.update_file("dados_logistica.csv", "Edit Financeiro", csv_editado, sha)
                st.success("Financeiro atualizado!")
                st.rerun()
