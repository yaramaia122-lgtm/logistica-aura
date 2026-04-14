import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 1. IDENTIDADE VISUAL RIGOROSA (AZUL MARINHO + OCRE + BRANCO)
st.set_page_config(
    page_title="Aura Minerals - Logística",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS para aplicar as cores exatas da imagem enviada
st.markdown("""
    <style>
    /* Fundo principal Branco Limpo */
    .stApp { background-color: #FFFFFF !important; }
    
    /* Barra Lateral - Azul Marinho Institucional */
    [data-testid="stSidebar"] {
        background-color: #002D5E !important; 
        border-right: 2px solid #FFC20E; /* Linha Ocre sutil */
    }
    
    /* Forçar todos os textos da barra lateral para Branco */
    [data-testid="stSidebar"] * { color: #FFFFFF !important; }
    
    /* EFEITO DE SOMBRA NA LOGO (GLOW) */
    .logo-glow {
        filter: drop-shadow(0px 0px 12px rgba(255, 255, 255, 0.4));
        margin-bottom: 25px;
    }
    
    /* Títulos e Rótulos em Azul Marinho para leitura no branco */
    h1, h2, h3, h4, label, p, span { 
        color: #002D5E !important; 
        font-family: 'Arial', sans-serif !important; 
    }
    
    /* Botões em Azul Marinho com borda Ocre */
    .stButton>button {
        background-color: #002D5E;
        color: #FFFFFF;
        border: 1px solid #FFC20E;
        border-radius: 4px;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #FFC20E;
        color: #002D5E;
    }
    
    /* Tabelas (Agenda) */
    .stTable { 
        background-color: #FFFFFF !important; 
        border: 1px solid #002D5E; 
    }
    </style>
    """, unsafe_allow_html=True)

# 2. GESTÃO DE DADOS (VERSÃO V18)
DB_V = "logistica_aura_v18_viagens.csv"
DB_P = "logistica_aura_v18_passageiros.csv"

def carregar_dados():
    if not os.path.exists(DB_V):
        pd.DataFrame(columns=["Data", "Motorista", "Passageiro", "CC", "Saida", "Voo", "Trajeto", "Hospedagem", "Observacao", "Hotel_RS", "Aereo_RS", "Combust_RS", "Total_RS"]).to_csv(DB_V, index=False)
    if not os.path.exists(DB_P):
        pd.DataFrame(columns=["Nome", "CC_Padrao"]).to_csv(DB_P, index=False)
    return pd.read_csv(DB_V).fillna(""), pd.read_csv(DB_P).fillna("")

df_v, df_p = carregar_dados()

# 3. SIDEBAR (LOGO E MENU)
with st.sidebar:
    # Div centralizada com a logo e a sombra solicitada
    st.markdown(f"""
        <div style="text-align: center; padding-top: 10px;">
            <img src="https://gist.githubusercontent.com/user-attachments/assets/8e0f5228-40b9-4674-9f0f-6df3d57b280c" 
                 width="190" class="logo-glow">
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    menu = st.radio(
        "PAINEL DE CONTROLE",
        ["📋 Agenda Motoristas", "📝 Programar Viagem", "👤 Cadastrar Viajante", "💰 Financeiro"]
    )
    st.markdown("---")
    st.caption("Aura Minerals Apoena | Logística")

# 4. MÓDULOS

if menu == "📋 Agenda Motoristas":
    st.header("Agenda de Viagens Operacionais")
    if not df_v.empty:
        agenda = df_v[["Data", "Motorista", "Passageiro", "Saida", "Voo", "Trajeto", "Hospedagem", "Observacao"]]
        st.table(agenda)
    else:
