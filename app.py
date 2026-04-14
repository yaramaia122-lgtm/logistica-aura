import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 1. CONFIGURAÇÃO DE LAYOUT (AZUL MARINHO E BRANCO)
st.set_page_config(page_title="Logística Aura Apoena", layout="wide", initial_sidebar_state="expanded")

# CSS para garantir que nada saia do lugar
st.markdown("""
    <style>
    /* Força Fundo Branco */
    .stApp { background-color: #FFFFFF !important; }
    
    /* Menu Lateral Azul Marinho Aura */
    [data-testid="stSidebar"] {
        background-color: #002D5E !important;
        border-right: 3px solid #FFC20E;
    }
    [data-testid="stSidebar"] * { color: #FFFFFF !important; }
    
    /* Efeito de Sombra na Logo */
    .logo-aura {
        filter: drop-shadow(0px 0px 10px rgba(255, 255, 255, 0.4));
        display: block;
        margin: auto;
        padding-bottom: 20px;
    }
    
    /* Títulos e botões */
    h1, h2, h3, h4, label { color: #002D5E !important; }
    .stButton>button {
        background-color: #002D5E;
        color: white;
        border: 1px solid #FFC20E;
        font-weight: bold;
    }
    .stTable { background-color: white !important; border: 1px solid #002D5E; }
    </style>
    """, unsafe_allow_html=True)

# 2. FUNÇÃO DE DADOS (SEM TRAVAR O SISTEMA)
DB_V = "logistica_viagens_v6.csv"
DB_P = "cadastro_passageiros_v6.csv"

def carregar_dados():
    # Garante que os arquivos existam com as colunas certas
    cols_v = ["Data", "Motorista", "Passageiro", "CC", "Saida", "Voo", "Trajeto", "Hospedagem", "Observacao"]
    if not os.path.exists(DB_V): pd.DataFrame(columns=cols_v).to_csv(DB_V, index=False)
    if not os.path.exists(DB_P): pd.DataFrame(columns=["Nome"]).to_csv(DB_P, index=False)
    
    v = pd.read_csv(DB_V).fillna("")
    p = pd.read_csv(DB_P).fillna("")
    return v, p

df_viagens, df_passageiros = carregar_dados()

# 3. BARRA LATERAL (LOGO E MENU)
with st.sidebar:
    # Link direto da imagem Aura com sombra
    st.markdown("""
        <div style="text-align: center;">
            <img src="https://gist.githubusercontent.com/user-attachments/assets/8e0f5228-40b9-4674-9f0f-6df3d57b280c" 
                 width="180" class="logo-aura">
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    menu = st.radio("NAVEGAÇÃO", ["📋 Agenda Motoristas", "📝 Programar Viagem", "👤 Cadastrar Viajante", "💰 Financeiro"])

# 4. MÓDULOS (LÓGICA SIMPLIFICADA PARA NÃO DAR ERRO)

if menu == "📋 Agenda Motoristas":
    st.header("Agenda Operacional")
    if not df_viagens.empty:
        # Tenta mostrar apenas as colunas que existirem para não dar erro de "KeyError"
        cols_mostrar = [c for c in ["Data", "Motorista", "Passageiro", "Saida", "Voo", "Trajeto", "Hospedagem", "Observacao"] if c in df_viagens.columns]
        st.table(df_viagens[cols_mostrar])
    else:
        st.info("Nenhuma viagem programada.")

elif menu == "📝 Programar Viagem":
    st.header("Nova Programação")
    if df_passageiros.empty:
        st.warning("Cadastre um viajante primeiro.")
    else:
        with st.form("nova_viagem"):
            p = st.selectbox("Passageiro", df_passageiros["Nome"].tolist())
            m = st.selectbox("Motorista", ["Ilson", "Antonio"])
            d = st.date_input("Data", datetime.now())
            sd = st.text_input("Saída")
            obs = st.text_area("Observação")
            if st.form_submit_button("✅ SALVAR"):
                nova = pd.DataFrame([{"Data": d.strftime('%d/%m/%Y'), "Motorista": m, "Passageiro": p, "Saida": sd, "Observacao": obs}])
                pd.concat([df_viagens, nova], ignore_index=True).to_csv(DB_V, index=False)
                st.success("Salvo!")
                st.rerun()

elif menu == "👤 Cadastrar Viajante":
    st.header("Cadastro de Funcionário")
    with st.form("novo_cadastro"):
        n = st.text_input("Nome Completo").upper()
        if st.form_submit_button("CADASTRAR"):
            if n:
                pd.concat([df_passageiros, pd.DataFrame([{"Nome": n}])], ignore_index=True).to_csv(DB_P, index=False)
                st.success(f"{n} cadastrado!")
                st.rerun()

elif menu == "💰 Financeiro":
    st.header("Financeiro")
    if not df_viagens.empty:
        df_ed = st.data_editor(df_viagens)
        if st.button("Salvar Alterações"):
            df_ed.to_csv(DB_V, index=False)
            st.success("Atualizado!")
