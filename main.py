import streamlit as st
import pandas as pd
from github import Github
import io
from datetime import datetime

# --- CONFIGURAÇÃO E IDIOMA ---
st.set_page_config(page_title="Aura Apoena Logistics", layout="wide")

# --- UI/UX DESIGNER (ESTILO CONGELADO) ---
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    [data-testid="stSidebar"] { background-color: #002D5E !important; min-width: 280px; }
    
    /* SOMBRA NA LOGO */
    [data-testid="stSidebar"] [data-testid="stImage"] img {
        filter: drop-shadow(0px 10px 15px rgba(0,0,0,0.7));
    }

    /* CAIXAS AZUL CLARO / LETRAS PRETAS */
    .stTextInput input, .stSelectbox div[data-baseweb="select"], .stDateInput input, .stNumberInput input {
        background-color: #F0F7FF !important; 
        border: 2px solid #002D5E !important;
        color: #000000 !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
    }
    
    /* Labels e Textos */
    label, .stMarkdown p { color: #002D5E !important; font-weight: bold !important; }
    input { color: #000000 !important; }

    /* BOTÕES PADRONIZADOS */
    div.stButton > button {
        background-color: #E1E8F0 !important;
        color: #002D5E !important;
        border: 2px solid #002D5E !important;
        font-weight: 700 !important;
        height: 50px !important;
        width: 100% !important;
    }
    div.stButton > button:hover { background-color: #002D5E !important; color: #E1E8F0 !important; }
    [data-testid="stSidebar"] .stMarkdown p, [data-testid="stSidebar"] label { color: #FFFFFF !important; }
    </style>
    """, unsafe_allow_html=True)

# --- BACKEND (ESTUDO DE ESTABILIDADE) ---
def carregar_sistema():
    colunas = ["Passageiro", "Motorista", "Data", "Trajeto", "Descricao", "Hotel", "Combustivel", "Aereo", "Outros", "Total"]
    try:
        g = Github(st.secrets["GITHUB_TOKEN"])
        repo = g.get_repo("yaramaia122-lgtm/logistica-aura")
        contents = repo.get_contents("dados_logistica.csv")
        df = pd.read_csv(io.StringIO(contents.decoded_content.decode()))
        # Garantia de colunas (estudo de apps escaláveis)
        for col in colunas:
            if col not in df.columns:
                df[col] = 0.0 if col in ["Hotel", "Combustivel", "Aereo", "Outros", "Total"] else ""
        return df, contents.sha, repo
    except:
        return pd.DataFrame(columns=colunas), None, None

df, sha, repo = carregar_sistema()

# --- MENU LATERAL ---
with st.sidebar:
    st.markdown("<br>", unsafe_allow_html=True)
    logo = "https://raw.githubusercontent.com/yaramaia122-lgtm/logistica-aura/main/logo.png"
    st.image(logo, width=220)
    st.markdown("<br>", unsafe_allow_html=True)
    menu = st.radio("NAVEGACAO", ["Agenda", "Programar Viagem", "Financeiro"])

# --- MODULOS ---

if menu == "Agenda":
    st.title("📋 Agenda de Viagens")
    if not df.empty:
        # Mostra apenas os dados de logística
        st.dataframe(df[["Passageiro", "Motorista", "Data", "Trajeto", "Descricao"]], use_container_width=True)
    else:
        st.info("Nenhuma viagem registrada.")

elif menu == "Programar Viagem":
    st.title("📝 Programar Viagem")
    with st.form("form_viagem", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            nome = st.text_input("Nome do Passageiro").upper()
            motorista = st.selectbox("Motorista", ["Ilson", "Antonio", "Outro"])
            v_hotel = st.number_input("Hotel (R$)", min_value=0.0)
            v_aereo = st.number_input("Aéreo (R$)", min_value=0.0)
        with c2:
            data = st.date_input("Data", datetime.now())
            trajeto = st.selectbox("Itinerário", ["P. Lacerda x Cuiabá", "Interno", "Outro"])
            v_comb = st.number_input("Combustível (R$)", min_value=0.0)
            v_outros = st.number_input("Outros Custos (R$)", min_value=0.0)
        
        # Lógica de descrição eficiente
        obs = st.text_input("Descrição / Observações")

        if st.form_submit_button("GRAVAR REGISTRO"):
            if nome and repo:
                total = v_hotel + v_comb + v_aereo + v_outros
                nova_vi
