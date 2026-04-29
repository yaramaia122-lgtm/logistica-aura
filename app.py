import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 1. VISUAL PADRÃO AURA (CINZA E AZUL MARINHO - SEM PRETO)
st.set_page_config(page_title="Logística Aura Minerals", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF !important; }
    [data-testid="stSidebar"] { background-color: #002D5E !important; }
    [data-testid="stSidebar"] * { color: #FFFFFF !important; }
    
    /* Inputs: Fundo Cinza, Letra Azul Marinho */
    div[data-baseweb="input"], input, select, textarea {
        background-color: #E8E8E8 !important;
        color: #002D5E !important;
        border: 1px solid #002D5E !important;
    }
    
    /* Botões: Estilo Profissional */
    .stButton>button {
        background-color: #E8E8E8 !important;
        color: #002D5E !important;
        border: 2px solid #002D5E !important;
        font-weight: bold; width: 100%;
    }
    .stButton>button:hover { background-color: #002D5E !important; color: #FFFFFF !important; }
    
    /* Tabela Financeira */
    [data-testid="stDataEditor"] { background-color: #E8E8E8 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. CAMINHO REAL DO SEU ONEDRIVE (A PONTE PARA O SHAREPOINT) ---
PASTA_ONEDRIVE = r"C:\Users\yara.chaves\OneDrive - Aura Minerals\Apoena - Gerência Administrativa e Financeira-Infraestrutura - Teste"

DB_V = os.path.join(PASTA_ONEDRIVE, "banco_viagens_oficial.csv")
# ------------------------------------------------------------------

def carregar_dados():
    if not os.path.exists(DB_V):
        # Cria o arquivo com as colunas caso ele não exista na sua pasta
        pd.DataFrame(columns=["Data", "Motorista", "Passageiro", "Saida", "Trajeto", "Valor"]).to_csv(DB_V, index=False)
    return pd.read_csv(DB_V).fillna("")

df_v = carregar_dados()

# 3. INTERFACE E MELHORIAS
with st.sidebar:
    st.markdown("### 🚛 Gestão de Logística")
    menu = st.radio("MENU", ["📋 Agenda", "📝 Programar Viagem", "💰 Financeiro"])

if menu == "📝 Programar Viagem":
    st.header("📝 Nova Programação")
    with st.form("form_viagem"):
        c1, c2 = st.columns(2)
        p = c1.text_input("Passageiro").upper()
        m = c1.selectbox("Motorista", ["Ilson", "Antonio"])
        d = c1.date_input("Data", datetime.now())
        t = c2.selectbox("Trajeto", ["P. LACERDA X CUIABÁ", "INTERNO", "OUTRO"])
        
        if st.form_submit_button("✅ SALVAR E SINCRONIZAR"):
            nova_linha = pd.DataFrame([{"Data": d.strftime('%d/%m/%Y'), "Motorista": m, "Passageiro": p, "Trajeto": t}])
            pd.concat([df_v, nova_linha], ignore_index=True).to_csv(DB_V, index=False)
            st.success("Salvo no seu OneDrive! O Power Automate fará o resto.")

elif menu == "💰 Financeiro":
    st.header("💰 Controle de Custos")
    # Melhoria: Tabela editável que salva direto no seu OneDrive
    df_editado = st.data_editor(df_v, use_container_width=True)
    if st.button("💾 ATUALIZAR PLANILHA"):
        df_editado.to_csv(DB_V, index=False)
        st.success("Planilha de custos atualizada com sucesso!")
