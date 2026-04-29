import streamlit as st
import pandas as pd
from github import Github
import io
from datetime import datetime

# Força o navegador a não traduzir (evita erros de Node)
st.markdown('<html lang="pt-br">', unsafe_allow_html=True)

st.set_page_config(page_title="Logística Apoena", layout="wide")

# CSS Simplificado e Robusto
st.markdown("""
    <style>
    .stApp { background-color: white; }
    [data-testid="stSidebar"] { background-color: #002D5E !important; }
    [data-testid="stSidebar"] * { color: white !important; }
    div.stButton > button { background-color: #E8E8E8; color: #002D5E; font-weight: bold; width: 100%; border: 1px solid #002D5E; }
    div.stButton > button:hover { background-color: #002D5E !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# Lógica de conexão
def get_data():
    try:
        g = Github(st.secrets["GITHUB_TOKEN"])
        repo = g.get_repo("yaramaia122-lgtm/logistica-aura")
        contents = repo.get_contents("dados_logistica.csv")
        df = pd.read_csv(io.StringIO(contents.decoded_content.decode()))
        return df, contents.sha, repo
    except:
        return pd.DataFrame(columns=["Passageiro", "Motorista", "Data", "Trajeto"]), None, None

df, sha, repo = get_data()

# Sidebar
with st.sidebar:
    st.image("https://raw.githubusercontent.com/yaramaia122-lgtm/logistica-aura/main/Aura%20(Azul%20e%20Ocre)%20(1).png")
    st.markdown("---")
    menu = st.radio("Menu", ["Agenda", "Programar", "Financeiro"])

if menu == "Programar":
    st.subheader("📝 Nova Viagem")
    with st.form("v"):
        p = st.text_input("Passageiro").upper()
        m = st.selectbox("Motorista", ["Ilson", "Antonio", "Outro"])
        d = st.date_input("Data", datetime.now())
        t = st.selectbox("Trajeto", ["P. Lacerda x Cuiabá", "Interno", "Outro"])
        if st.form_submit_button("Salvar"):
            if p and repo:
                novo = pd.DataFrame([[p, m, d.strftime('%d/%m/%Y'), t]], columns=df.columns)
                df_f = pd.concat([df, novo], ignore_index=True)
                csv = df_f.to_csv(index=False)
                if sha: repo.update_file("dados_logistica.csv", "up", csv, sha)
                else: repo.create_file("dados_logistica.csv", "init", csv)
                st.success("Salvo!"); st.rerun()

elif menu == "Agenda":
    st.subheader("📋 Agenda")
    st.table(df)

elif menu == "Financeiro":
    st.subheader("💰 Editar")
    ed = st.data_editor(df, num_rows="dynamic", use_container_width=True)
    if st.button("Salvar Alterações"):
        if repo:
            csv = ed.to_csv(index=False)
            repo.update_file("dados_logistica.csv", "edit", csv, sha)
            st.success("Atualizado!"); st.rerun()
