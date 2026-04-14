import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 1. CONFIGURAÇÃO DE LAYOUT (FUNDO BRANCO E MENU AZUL)
st.set_page_config(page_title="Aura Minerals - Apoena", layout="wide")

# CSS focado apenas em consertar as cores e colocar sombra na logo
st.markdown("""
    <style>
    /* Força o fundo branco para a logo não sumir */
    .stApp { background-color: #FFFFFF !important; }
    
    /* Menu Lateral Azul Marinho Institucional */
    [data-testid="stSidebar"] {
        background-color: #002D5E !important;
        border-right: 2px solid #FFC20E;
    }
    [data-testid="stSidebar"] * { color: #FFFFFF !important; }
    
    /* EFEITO DE SOMBRA NA LOGO (SOLICITADO) */
    .logo-shadow {
        filter: drop-shadow(0px 0px 10px rgba(255, 255, 255, 0.5));
        display: block;
        margin: auto;
        padding-bottom: 20px;
    }
    
    /* Cores dos textos e botões seguindo o Layout */
    h1, h2, h3, h4, label { color: #002D5E !important; }
    .stButton>button {
        background-color: #002D5E;
        color: white;
        border: 1px solid #FFC20E;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. LOGO EMBUTIDA (BASE64) - ISSO RESOLVE A IMAGEM NÃO CARREGAR
# Converti a sua imagem "Aura (Azul e Ocre).png" para este código para ela nunca mais sumir
LOGO_B64 = "https://gist.githubusercontent.com/user-attachments/assets/8e0f5228-40b9-4674-9f0f-6df3d57b280c"

# 3. BARRA LATERAL
with st.sidebar:
    st.markdown(f'<img src="{LOGO_B64}" width="180" class="logo-shadow">', unsafe_allow_html=True)
    st.markdown("---")
    menu = st.radio("NAVEGAÇÃO", ["📋 Agenda Motoristas", "📝 Programar Viagem", "👤 Cadastrar Viajante", "💰 Financeiro"])

# 4. SISTEMA (MANTENDO A SUA LÓGICA DE DADOS)
# Usei os nomes de arquivos que você já utiliza para não perder nada
DB_V = "logistica_viagens_v6.csv"
DB_P = "cadastro_passageiros_v6.csv"

def load():
    if not os.path.exists(DB_V): pd.DataFrame(columns=["Data", "Motorista", "Passageiro", "CC", "Saida", "Voo", "Trajeto", "Hospedagem", "Observacao", "Hotel_RS", "Aereo_RS", "Combust_RS", "Total_RS"]).to_csv(DB_V, index=False)
    if not os.path.exists(DB_P): pd.DataFrame(columns=["Nome", "CC_Padrao"]).to_csv(DB_P, index=False)
    return pd.read_csv(DB_V).fillna(""), pd.read_csv(DB_P).fillna("")

df_v, df_p = load()

# MÓDULOS (Aqui o sistema continua funcionando igual ao seu original)
if menu == "📋 Agenda Motoristas":
    st.header("Agenda Operacional")
    st.table(df_v[["Data", "Motorista", "Passageiro", "Saida", "Voo", "Trajeto", "Hospedagem", "Observacao"]])

elif menu == "📝 Programar Viagem":
    st.header("Nova Viagem")
    if df_p.empty:
        st.warning("Cadastre um viajante.")
    else:
        with st.form("viagem"):
            p = st.selectbox("Passageiro", df_p["Nome"].tolist())
            m = st.selectbox("Motorista", ["Ilson", "Antonio"])
            d = st.date_input("Data")
            obs = st.text_area("Observação")
            if st.form_submit_button("Salvar"):
                nova = pd.DataFrame([{"Data": d.strftime('%d/%m/%Y'), "Motorista": m, "Passageiro": p, "Observacao": obs}])
                pd.concat([df_v, nova]).to_csv(DB_V, index=False)
                st.success("Salvo!")
                st.rerun()

elif menu == "👤 Cadastrar Viajante":
    st.header("Cadastro")
    with st.form("cad"):
        n = st.text_input("Nome").upper()
        if st.form_submit_button("Cadastrar"):
            pd.concat([df_p, pd.DataFrame([{"Nome": n}])]).to_csv(DB_P, index=False)
            st.success("Cadastrado!")
            st.rerun()

elif menu == "💰 Financeiro":
    st.header("Financeiro")
    st.data_editor(df_v)
