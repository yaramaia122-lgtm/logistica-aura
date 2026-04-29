import streamlit as st
import pandas as pd
from github import Github
import io
from datetime import datetime

# 1. CONFIGURAÇÃO
st.set_page_config(page_title="Aura Logistics", layout="wide")
st.markdown('<html lang="pt-br">', unsafe_allow_html=True)

# 2. DESIGN SEGURO (SEM QUEBRAS DE LINHA QUE CAUSAM ERRO)
st.markdown("<style>.stApp {background-color: #FFFFFF;} [data-testid='stSidebar'] {background-color: #002D5E !important;} [data-testid='stSidebar'] [data-testid='stImage'] img {filter: drop-shadow(0px 10px 15px rgba(0,0,0,0.7));} .stTextInput input, .stSelectbox div[data-baseweb='select'], .stDateInput input, .stNumberInput input {background-color: #F0F7FF !important; border: 1px solid #002D5E !important; color: #000000 !important; border-radius: 6px !important;} input, div[data-baseweb='select'] span {color: #000000 !important;} label, .stMarkdown p {color: #002D5E !important; font-weight: bold !important;} div.stButton > button {background-color: #E1E8F0 !important; color: #002D5E !important; border: 1px solid #002D5E !important; font-weight: 700 !important; width: 100% !important; height: 50px !important;} [data-testid='stSidebar'] .stMarkdown p, [data-testid='stSidebar'] label {color: #FFFFFF !important;}</style>", unsafe_allow_html=True)

# 3. BANCO DE DADOS
def carregar_dados():
    cols = ["Passageiro", "Motorista", "Data", "Trajeto", "Obs", "Hotel", "Combustivel", "Aereo", "Outros", "Total"]
    try:
        g = Github(st.secrets["GITHUB_TOKEN"])
        repo = g.get_repo("yaramaia122-lgtm/logistica-aura")
        contents = repo.get_contents("dados_logistica.csv")
        df = pd.read_csv(io.StringIO(contents.decoded_content.decode()))
        for c in cols:
            if c not in df.columns: df[c] = 0.0 if c in ["Hotel", "Combustivel", "Aereo", "Outros", "Total"] else ""
        return df, contents.sha, repo
    except:
        return pd.DataFrame(columns=cols), None, None

df, sha, repo = carregar_dados()

# 4. SIDEBAR
with st.sidebar:
    st.markdown("<br>", unsafe_allow_html=True)
    st.image("https://raw.githubusercontent.com/yaramaia122-lgtm/logistica-aura/main/logo.png", width=220)
    st.markdown("---")
    menu = st.radio("MENU", ["Agenda", "Programar Viagem", "Financeiro"])

# 5. TELAS
if menu == "Agenda":
    st.title("📋 Agenda de Viagens")
    st.dataframe(df[["Passageiro", "Motorista", "Data", "Trajeto", "Obs"]], use_container_width=True)

elif menu == "Programar Viagem":
    st.title("📝 Programar Viagem")
    with st.form("form_v", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            pax = st.text_input("Nome").upper()
            mot = st.selectbox("Motorista", ["Ilson", "Antonio", "Outro"])
            v_h = st.number_input("Hotel (R$)", min_value=0.0)
        with c2:
            dt = st.date_input("Data", datetime.now())
            tr = st.selectbox("Itinerario", ["P. Lacerda x Cuiaba", "Interno", "Outro"])
            v_c = st.number_input("Combustivel (R$)", min_value=0.0)
        
        v_a = st.number_input("Aereo (R$)", min_value=0.0)
        v_o = st.number_input("Outros (R$)", min_value=0.0)
        obs = st.text_input("Observacoes")

        if st.form_submit_button("GRAVAR REGISTRO"):
            if pax and repo:
                total = v_h + v_c + v_a + v_o
                nova = pd.DataFrame([[pax, mot, dt.strftime('%d/%m/%Y'), tr, obs, v_h, v_c, v_a, v_o, total]], columns=df.columns)
                df_up = pd.concat([df, nova], ignore_index=True)
                repo.update_file("dados_logistica.csv", "Update", df_up.to_csv(index=False), sha)
                st.success("✅ VIAGEM PROGRAMADA")
                st.rerun()

elif menu == "Financeiro":
    st.title("💰 Financeiro")
    df_ed = st.data_editor(df, num_rows="dynamic", use_container_width=True)
    if st.button("SALVAR ALTERACOES"):
        if repo:
            df_ed["Total"] = df_ed["Hotel"] + df_ed["Combustivel"] + df_ed["Aereo"] + df_ed["Outros"]
            repo.update_file("dados_logistica.csv", "Edit", df_ed.to_csv(index=False), sha)
            st.success("✅ ALTERACOES REGISTRADAS")
            st.rerun()
