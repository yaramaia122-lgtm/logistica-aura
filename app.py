import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 1. IDENTIDADE VISUAL COMPLETA (AZUL MARINHO, OCRE E BRANCO)
st.set_page_config(page_title="Logística Aura Minerals", layout="wide")

st.markdown("""
    <style>
    /* Forçar Fundo Branco */
    .stApp { background-color: #FFFFFF !important; }
    
    /* Barra Lateral Azul Marinho Aura */
    [data-testid="stSidebar"] {
        background-color: #002D5E !important;
        border-right: 3px solid #FFC20E;
    }
    [data-testid="stSidebar"] * { color: #FFFFFF !important; }
    
    /* Efeito de Sombra na Logo */
    .logo-aura {
        filter: drop-shadow(0px 4px 10px rgba(255, 255, 255, 0.4));
        display: block; margin: auto; padding-bottom: 20px;
    }
    
    /* AZUL EM TODAS AS FONTES DO SISTEMA (Maiores e Menores) */
    h1, h2, h3, h4, p, span, label, div, small { 
        color: #002D5E !important; 
        font-family: 'Arial', sans-serif !important; 
    }
    
    /* Ajuste específico para rótulos de campos (letras menores) */
    .stTextInput label, .stSelectbox label, .stDateInput label, .stTextArea label {
        color: #002D5E !important;
        font-weight: bold !important;
        font-size: 14px !important;
    }

    /* Botões Padrão Aura */
    .stButton>button {
        background-color: #002D5E; color: white !important;
        border: 2px solid #FFC20E; border-radius: 5px;
        font-weight: bold; height: 3em; width: 100%;
    }
    .stButton>button:hover {
        background-color: #FFC20E; color: #002D5E !important;
    }
    
    /* Estilo das Tabelas */
    .stTable { background-color: white !important; border: 1px solid #002D5E; }
    </style>
    """, unsafe_allow_html=True)

# 2. BANCO DE DADOS LOCAL (PERSISTÊNCIA)
DB_VIAGENS = "data_viagens_v33.csv"
DB_PASSAGEIROS = "data_passageiros_v33.csv"

def inicializar_arquivos():
    cols_v = ["Data", "Motorista", "Passageiro", "CC", "Saida", "Voo", "Trajeto", "Hospedagem", "Observacao"]
    cols_p = ["Nome", "Centro_Custo"]
    
    if not os.path.exists(DB_VIAGENS): pd.DataFrame(columns=cols_v).to_csv(DB_VIAGENS, index=False)
    if not os.path.exists(DB_PASSAGEIROS): pd.DataFrame(columns=cols_p).to_csv(DB_PASSAGEIROS, index=False)
    
    v = pd.read_csv(DB_VIAGENS).fillna("")
    p = pd.read_csv(DB_PASSAGEIROS).fillna("")
    return v, p

df_v, df_p = inicializar_arquivos()

LISTA_CC = sorted(["210301 - Moagem", "210403 - Detox", "210801 - Laboratório", "211002 - Manut. Mecânica", "320301 - RH", "310501 - Meio Ambiente"])

# 3. BARRA LATERAL
with st.sidebar:
    st.markdown("""<div style="text-align: center;"><img src="https://gist.githubusercontent.com/user-attachments/assets/8e0f5228-40b9-4674-9f0f-6df3d57b280c" width="180" class="logo-aura"></div>""", unsafe_allow_html=True)
    st.markdown("---")
    menu = st.radio("MÓDULOS OPERACIONAIS", ["📋 Agenda Motoristas", "📝 Programar Viagem", "👤 Cadastrar Viajante", "💰 Financeiro"])
    st.markdown("---")
    st.write(f"📊 **Monitor:** {len(df_v)} viagens / {len(df_p)} passageiros")

# 4. MÓDULOS

if menu == "📋 Agenda Motoristas":
    st.header("📋 Agenda Operacional de Viagens")
    if not df_v.empty:
        st.dataframe(df_v, use_container_width=True, hide_index=True)
    else:
        st.warning("Agenda vazia. Cadastre uma viagem para visualizar.")

elif menu == "📝 Programar Viagem":
    st.header("📝 Detalhamento de Nova Viagem")
    if df_p.empty:
        st.error("❌ Ação Necessária: Cadastre um passageiro para habilitar este formulário.")
    else:
        with st.form("form_v33", clear_on_submit=True):
            col1, col2 = st.columns(2)
            p_sel = col1.selectbox("Selecione o Passageiro*", sorted(df_p["Nome"].tolist()))
            mot_v = col1.selectbox("Motorista*", ["Ilson", "Antonio"])
            data_v = col1.date_input("Data da Missão", datetime.now())
            
            saida_v = col2.text_input("Horário de Saída*")
            voo_v = col2.text_input("Voo / Conexão")
            hosp_v = col2.text_input("Local de Hospedagem")
            
            st.write("---")
            traj_v = st.selectbox("Trajeto Sugerido", ["P. LACERDA X CUIABÁ", "CUIABÁ X P. LACERDA", "INTERNO", "OUTRO"])
            cc_v = st.selectbox("Centro de Custo (Rateio)", LISTA_CC)
            obs_v = st.text_area("Instruções Adicionais para o Motorista")
