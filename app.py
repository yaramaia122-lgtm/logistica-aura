import streamlit as st
import pandas as pd
import os
from datetime import datetime
import base64

# 1. ESTILO AURA (FUNDO BRANCO E CORES OFICIAIS)
st.set_page_config(page_title="Logística Aura Apoena", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: white !important; }
    [data-testid="stSidebar"] { background-color: #002D5E !important; }
    [data-testid="stSidebar"] * { color: white !important; }
    h1, h2, h3, h4, label, p, span { color: #002D5E !important; }
    .stButton>button { background-color: #002D5E; color: white; border: 2px solid #FFC20E; }
    .stDownloadButton>button { background-color: #FFC20E !important; color: #002D5E !important; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 2. CARREGAR LOGO QUE VOCÊ ENVIOU
def carregar_logo(nome_arquivo):
    if os.path.exists(nome_arquivo):
        with open(nome_arquivo, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

# 3. BANCO DE DADOS (VERSÃO V12)
DB_V = "logistica_v12_viagens.csv"
DB_P = "logistica_v12_passageiros.csv"

def iniciar():
    if not os.path.exists(DB_V):
        pd.DataFrame(columns=["Data", "Motorista", "Passageiro", "CC", "Saida", "Voo", "Trajeto", "Hospedagem", "Observacao", "Hotel_RS", "Aereo_RS", "Combust_RS", "Total_RS"]).to_csv(DB_V, index=False)
    if not os.path.exists(DB_P):
        pd.DataFrame(columns=["Nome", "CC_Padrao"]).to_csv(DB_P, index=False)
    return pd.read_csv(DB_V).fillna(""), pd.read_csv(DB_P).fillna("")

df_v, df_p = iniciar()

# 4. MENU LATERAL (SIDEBAR)
with st.sidebar:
    logo_b64 = carregar_logo("Aura (Azul e Ocre).png")
    if logo_b64:
        st.markdown(f'<img src="data:image/png;base64,{logo_b64}" width="200">', unsafe_allow_html=True)
    else:
        st.markdown("<h2 style='color: #FFC20E;'>Aura Apoena</h2>", unsafe_allow_html=True)
    
    st.markdown("---")
    menu = st.radio("MENU", ["📋 Agenda Motoristas", "📝 Programar Viagem", "👤 Cadastrar Viajante", "💰 Financeiro"])

# 5. MÓDULOS
if menu == "📋 Agenda Motoristas":
    st.header("Agenda de Viagens")
    if not df_v.empty:
        st.table(df_v[["Data", "Motorista", "Passageiro", "Saida", "Voo", "Trajeto", "Hospedagem", "Observacao"]])
    else: st.info("Nenhuma viagem programada.")

elif menu == "📝 Programar Viagem":
    st.header("Nova Programação")
    if df_p.empty:
        st.warning("Cadastre um viajante primeiro.")
    else:
        nome_sel = st.selectbox("Passageiro", sorted(df_p["Nome"].tolist()))
        with st.form("f_v12"):
            data = st.date_input("Data")
            mot = st.selectbox("Motorista", ["Ilson", "Antonio"])
            hosp = st.text_input("Hotel/Destino")
            obs = st.text_area("Observações")
            if st.form_submit_button("Salvar Viagem"):
                nova = pd.DataFrame([{"Data": data.strftime('%d/%m/%Y'), "Motorista": mot, "Passageiro": nome_sel, "CC": "Rateio", "Saida": "-", "Voo": "-", "Trajeto": "-", "Hospedagem": hosp, "Observacao": obs, "Hotel_RS": 0.0, "Aereo_RS": 0.0, "Combust_RS": 0.0, "Total_RS": 0.0}])
                pd.concat([df_v, nova], ignore_index=True).to_csv(DB_V, index=False)
                st.success("✅ Salvo!")
                st.rerun()

elif menu == "👤 Cadastrar Viajante":
    st.header("Cadastrar Funcionário")
    with st.form("f_p12"):
        n = st.text_input("Nome").upper()
        if st.form_submit_button("Cadastrar"):
            if n:
                pd.concat([df_p, pd.DataFrame([{"Nome": n, "CC_Padrao": "Geral"}])], ignore_index=True).to_csv(DB_P, index=False)
                st.success(f"{n} cadastrado!")
                st.rerun()

elif menu == "💰 Financeiro":
    st.header("Financeiro")
    st.data_editor(df_v)
