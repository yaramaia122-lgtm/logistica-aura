import streamlit as st
import pandas as pd
import os
from datetime import datetime
import base64

# 1. FORÇAR TEMA CLARO E CORES AURA (STYLEGUIDE)
st.set_page_config(page_title="Aura Minerals - Logística", layout="wide")

st.markdown("""
    <style>
    /* Bloquear Modo Escuro */
    .stApp { background-color: white !important; }
    [data-testid="stSidebar"] { background-color: #002D5E !important; }
    [data-testid="stSidebar"] * { color: white !important; }
    
    /* Textos em Azul Aura */
    h1, h2, h3, h4, label, p, span { color: #002D5E !important; font-family: 'Benton Sans', sans-serif; }
    
    /* Botões */
    .stButton>button { background-color: #002D5E; color: white; border: 2px solid #FFC20E; }
    .stDownloadButton>button { background-color: #FFC20E !important; color: #002D5E !important; font-weight: bold; }
    
    /* Tabelas Brancas */
    .stTable { background-color: white !important; border: 1px solid #002D5E; }
    </style>
    """, unsafe_allow_html=True)

# 2. FUNÇÃO PARA CARREGAR IMAGEM LOCAL COM SEGURANÇA
def get_base64_img(img_path):
    if os.path.exists(img_path):
        with open(img_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return None

# 3. BANCO DE DADOS (NOMES NOVOS PARA EVITAR CONFLITOS)
DB_V = "logistica_aura_v7.csv"
DB_P = "passageiros_aura_v7.csv"

def carregar_dados():
    if not os.path.exists(DB_V):
        pd.DataFrame(columns=["Data", "Motorista", "Passageiro", "CC", "Saida", "Voo", "Trajeto", "Hospedagem", "Observacao", "Hotel_RS", "Aereo_RS", "Combust_RS", "Total_RS"]).to_csv(DB_V, index=False)
    if not os.path.exists(DB_P):
        pd.DataFrame(columns=["Nome", "CC_Padrao"]).to_csv(DB_P, index=False)
    return pd.read_csv(DB_V).fillna(""), pd.read_csv(DB_P).fillna("")

df_v, df_p = carregar_dados()

# LISTA OFICIAL DE CC
LISTA_CC = sorted([
    "210301 - Moagem", "210403 - Detox", "210801 - Laboratório", "211002 - Manut. Mecânica",
    "210405 - Lixiviação Planta", "210101 - Admin. Planta", "211001 - Manut. Elétrica",
    "320101 - Suprimentos", "320301 - RH", "121101 - Geologia Ernesto", "151101 - Geologia Nosde",
    "310501 - Meio Ambiente", "310503 - Segurança Trabalho", "310502 - Saúde"
])

# 4. SIDEBAR COM A LOGO (AURA AZUL E OCRE)
with st.sidebar:
    # Tenta carregar o arquivo que você subiu no GitHub
    img_b64 = get_base64_img("Aura (Azul e Ocre).png")
    if img_b64:
        st.markdown(f'<img src="data:image/png;base64,{img_b64}" width="200">', unsafe_allow_html=True)
    else:
        st.subheader("Aura Minerals") # Fallback se a imagem falhar
    
    st.markdown("---")
    menu = st.radio("MENU", ["📋 Agenda Motoristas", "📝 Programar Viagem", "👤 Cadastrar Viajante", "💰 Financeiro"])

# 5. MÓDULOS

if menu == "📋 Agenda Motoristas":
    st.header("Agenda Operacional")
    if not df_v.empty:
        # Layout limpo para o motorista
        agenda = df_v[["Data", "Motorista", "Passageiro", "Saida", "Voo", "Trajeto", "Hospedagem", "Observacao"]]
        st.table(agenda)
        csv = agenda.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 Baixar Agenda (CSV)", csv, "agenda_motoristas.csv", "text/csv")
    else: st.info("Sem viagens.")

elif menu == "📝 Programar Viagem":
    st.header("Nova Programação")
    if df_p.empty:
        st.warning("Cadastre um viajante primeiro.")
    else:
        nome_sel = st.selectbox("Passageiro", sorted(df_p["Nome"].tolist()))
        # Busca segura do CC
        cc_row = df_p[df_p["Nome"] == nome_sel]["CC_Padrao"]
        cc_sug = cc_row.iloc[0] if not cc_row.empty else LISTA_
