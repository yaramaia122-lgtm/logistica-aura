import streamlit as st
import pandas as pd
import os
from datetime import datetime
import base64

# 1. CONFIGURAÇÃO VISUAL (AZUL AURA + FUNDO BRANCO)
st.set_page_config(
    page_title="Aura Minerals - Logística",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS para forçar o Azul Marinho e Fundo Branco conforme o Layout da empresa
st.markdown("""
    <style>
    /* Fundo principal sempre branco */
    .stApp { background-color: #FFFFFF !important; }
    
    /* Menu Lateral - Azul Marinho Aura */
    [data-testid="stSidebar"] {
        background-color: #002D5E !important; 
        border-right: 3px solid #FFC20E;
    }
    [data-testid="stSidebar"] * { color: #FFFFFF !important; }
    
    /* Efeito de sombra e destaque na logo */
    .logo-container {
        text-align: center;
        padding-bottom: 20px;
    }
    .logo-shadow {
        filter: drop-shadow(0px 0px 10px rgba(255, 255, 255, 0.3));
    }
    
    /* Títulos em Azul para leitura clara no branco */
    h1, h2, h3, h4, label, p, span { 
        color: #002D5E !important; 
        font-family: 'Arial', sans-serif !important; 
    }
    
    /* Botões em Azul com borda Dourada */
    .stButton>button {
        background-color: #002D5E;
        color: #FFFFFF;
        border: 2px solid #FFC20E;
        border-radius: 4px;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #FFC20E;
        color: #002D5E;
    }
    
    /* Tabelas limpas com bordas sutis */
    .stTable { 
        background-color: white !important; 
        border: 1px solid #002D5E; 
    }
    </style>
    """, unsafe_allow_html=True)

# 2. GESTÃO DE DADOS (VERSÃO V16)
DB_V = "logistica_aura_v16_viagens.csv"
DB_P = "logistica_aura_v16_passageiros.csv"

def carregar_dados():
    if not os.path.exists(DB_V):
        pd.DataFrame(columns=["Data", "Motorista", "Passageiro", "CC", "Saida", "Voo", "Trajeto", "Hospedagem", "Observacao", "Hotel_RS", "Aereo_RS", "Combust_RS", "Total_RS"]).to_csv(DB_V, index=False)
    if not os.path.exists(DB_P):
        pd.DataFrame(columns=["Nome", "CC_Padrao"]).to_csv(DB_P, index=False)
    return pd.read_csv(DB_V).fillna(""), pd.read_csv(DB_P).fillna("")

df_v, df_p = carregar_dados()

LISTA_CC = sorted([
    "210301 - Moagem", "210403 - Detox", "210801 - Laboratório", "211002 - Manut. Mecânica",
    "210405 - Lixiviação", "210101 - Admin. Planta", "320101 - Suprimentos", "320301 - RH"
])

# 3. SIDEBAR (MENU AZUL COM LOGO)
with st.sidebar:
    # Div com a logo e a sombra solicitada
    st.markdown("""
        <div class="logo-container">
            <img src="https://gist.githubusercontent.com/user-attachments/assets/8e0f5228-40b9-4674-9f0f-6df3d57b280c" width="180" class="logo-shadow">
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    opcao = st.radio(
        "MENU DE NAVEGAÇÃO",
        ["📋 Agenda Motoristas", "📝 Programar Viagem", "👤 Cadastrar Viajante", "💰 Financeiro"]
    )
    st.markdown("---")
    st.caption("Aura Minerals Apoena | v16.0")

# 4. MÓDULOS

if opcao == "📋 Agenda Motoristas":
    st.header("Agenda Operacional")
    if not df_v.empty:
        # Tabela limpa para visualização rápida
        agenda = df_v[["Data", "Motorista", "Passageiro", "Saida", "Voo", "Trajeto", "Hospedagem", "Observacao"]]
        st.table(agenda)
    else:
        st.info("Nenhuma viagem programada.")

elif opcao == "📝 Programar Viagem":
    st.header("Nova Programação")
    if df_p.empty:
        st.warning("Cadastre um viajante primeiro.")
    else:
        passag_lista = sorted(df_p["Nome"].tolist())
        p_sel = st.selectbox("Selecione o Passageiro", passag_lista)
        
        with st.form("form_v16", clear_on_submit=True):
            col1, col2 = st.columns(2)
            data_v = col1.date_input("Data da Viagem", datetime.now())
            mot_v = col1.selectbox("Motorista", ["Ilson", "Antonio"])
            saida_v = col1.text_input("Horário Saída")
            voo_v = col2.text_input("Voo / Horário")
            hosp_v = col2.text_input("Hotel / Destino")
            obs_v = st.text_area("Observações para o Motorista")
            
            if st.form_submit_button("✅ SALVAR VIAGEM"):
                nova = pd.DataFrame([{
                    "Data": data_v.strftime('%d/%m/%Y'), "Motorista": mot_v, "Passageiro": p_sel, 
                    "CC": "Rateio", "Saida": saida_v, "Voo": voo_v, "Trajeto": "-", "Hospedagem": hosp_v,
                    "Observacao": obs_v, "Hotel_RS": 0.0, "Aereo_RS": 0.0, "Combust_RS": 0.0, "Total_RS": 0.0
                }])
                pd.concat([df_v, nova], ignore_index=True).to_csv(DB_V, index=False)
                st.success("Viagem registrada na agenda!")
                st.rerun()

elif opcao == "👤 Cadastrar Viajante":
    st.header("Cadastro de Funcionário")
    with st.form("cad_v16"):
        n = st.text_input("Nome Completo").upper()
        if st.form_submit_button("CADASTRAR"):
            if n:
                pd.concat([df_p, pd.DataFrame([{"Nome": n, "CC_Padrao": "Geral"}])], ignore_index=True).to_csv(DB_P, index=False)
                st.success(f"Cadastro de {n} realizado!")
                st.rerun()

elif opcao == "💰 Financeiro":
    st.header("Gestão Financeira")
    if not df_v.empty:
        df_ed = st.data_editor(df_v)
        if st.button("Salvar Alterações"):
            df_ed.to_csv(DB_V, index=False)
            st.success("Dados atualizados!")
