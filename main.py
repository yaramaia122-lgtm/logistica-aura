import streamlit as st
import pandas as pd
from github import Github
import io
from datetime import datetime

# 1. TRADUTOR E CONFIGURAÇÃO
st.markdown('<html lang="pt-br">', unsafe_allow_html=True)
st.set_page_config(page_title="Aura Apoena Logistics", layout="wide")

# 2. UI/UX - DESIGN PADRONIZADO (SOMBRA NA LOGO E CORES SOLICITADAS)
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    [data-testid="stSidebar"] { background-color: #002D5E !important; min-width: 280px; }
    
    /* Efeito de Sombra na Logo */
    [data-testid="stSidebar"] [data-testid="stImage"] img {
        filter: drop-shadow(0px 10px 15px rgba(0,0,0,0.7));
    }

    /* Inputs: Azul Claro com Letras Pretas */
    .stTextInput input, .stSelectbox div[data-baseweb="select"], .stDateInput input, .stNumberInput input {
        background-color: #F0F7FF !important; 
        border: 2px solid #002D5E !important;
        color: #000000 !important;
        border-radius: 8px !important;
    }
    
    input, div[data-baseweb="select"] span { color: #000000 !important; font-weight: 500 !important; }

    /* Labels e Botões */
    label, .stMarkdown p { color: #002D5E !important; font-weight: bold !important; }
    div.stButton > button {
        background-color: #E1E8F0 !important;
        color: #002D5E !important;
        border: 2px solid #002D5E !important;
        font-weight: 700 !important;
        width: 100% !important;
        height: 50px !important;
    }
    div.stButton > button:hover { background-color: #002D5E !important; color: #E1E8F0 !important; }
    [data-testid="stSidebar"] .stMarkdown p, [data-testid="stSidebar"] label { color: #FFFFFF !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. BACKEND - CONEXÃO GITHUB
def carregar_dados():
    cols = ["Passageiro", "Motorista", "Data", "Trajeto", "Obs Itinerário", "Hotel (R$)", "Combustível (R$)", "Aéreo (R$)", "Outros (R$)", "Total (R$)"]
    try:
        g = Github(st.secrets["GITHUB_TOKEN"])
        repo = g.get_repo("yaramaia122-lgtm/logistica-aura")
        contents = repo.get_contents("dados_logistica.csv")
        df = pd.read_csv(io.StringIO(contents.decoded_content.decode()))
        for c in cols:
            if c not in df.columns: df[c] = 0.0 if "R$" in c else ""
        return df, contents.sha, repo
    except:
        return pd.DataFrame(columns=cols), None, None

df, sha, repo = carregar_dados()

# 4. MENU LATERAL
with st.sidebar:
    st.markdown("<br>", unsafe_allow_html=True)
    # Logo oficial
    logo_url = "https://raw.githubusercontent.com/yaramaia122-lgtm/logistica-aura/main/logo.png"
    st.image(logo_url, width=220)
    st.markdown("<br>", unsafe_allow_html=True)
    menu = st.radio("NAVEGAÇÃO:", ["📋 Agenda", "📝 Programar Viagem", "💰 Financeiro"])

# 5. MÓDULOS

if menu == "📋 Agenda":
    st.title("📋 Agenda de Viagens")
    if not df.empty:
        st.dataframe(df[["Passageiro", "Motorista", "Data", "Trajeto", "Obs Itinerário"]], use_container_width=True)
    else:
        st.info("Nenhum registro encontrado.")

elif menu == "📝 Programar Viagem":
    st.title("📝 Programar Viagem")
    with st.form("form_viagem", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            pax = st.text_input("Nome do Passageiro").upper()
            mot = st.selectbox("Motorista", ["Ilson", "Antonio", "Outro"])
            v_h = st.number_input("Valor Hotel (R$)", min_value=0.0)
            v_a = st.number_input("Valor Aéreo (R$)", min_value=0.0)
        with c2:
            dt = st.date_input("Data", datetime.now())
            traj = st.selectbox("Itinerário Principal", ["P. Lacerda x Cuiabá", "Interno", "Outro"])
            v_c = st.number_input("Valor Combustível (R$)", min_value=0.0)
            v_o = st.number_input("Outros Custos (R$)", min_value=0.0)
        
        # Campo de descrição condicional
        lbl = "Descreva o Itinerário (Outro)" if traj == "Outro" else "Observações Adicionais"
        obs = st.text_input(lbl)

        if st.form_submit_button("GRAVAR REGISTRO"):
            if pax and repo:
                total = v_h + v_c + v_a + v_o
                nova = pd.DataFrame([[pax, mot, dt.strftime('%d/%m/%Y'), traj, obs, v_h, v_c, v_a, v_o, total]], columns=df.columns)
                df_up = pd.concat([df, nova], ignore_index=True)
                csv_txt = df_up.to_csv(index=False)
                
                if sha:
                    repo.update_file("
