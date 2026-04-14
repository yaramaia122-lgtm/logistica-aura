import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 1. CONFIGURAÇÃO VISUAL (PADRÃO AURA MINERALS)
st.set_page_config(
    page_title="Logística Aura Apoena",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS para forçar o layout institucional e a sombra na logo
st.markdown("""
    <style>
    /* Fundo principal sempre branco */
    .stApp { background-color: #FFFFFF !important; }
    
    /* Barra Lateral - Azul Marinho Aura */
    [data-testid="stSidebar"] {
        background-color: #002D5E !important; 
        border-right: 2px solid #FFC20E;
    }
    [data-testid="stSidebar"] * { color: #FFFFFF !important; }
    
    /* SOMBRA NA LOGO (GLOW) */
    .logo-aura {
        filter: drop-shadow(0px 0px 10px rgba(255, 255, 255, 0.4));
        margin-bottom: 25px;
        display: block;
        margin-left: auto;
        margin-right: auto;
    }
    
    /* Cores Institucionais nos Textos */
    h1, h2, h3, h4, label, p, span { 
        color: #002D5E !important; 
        font-family: 'Arial', sans-serif !important; 
    }
    
    /* Botões Azul com borda Ocre */
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
    
    /* Estilo das Tabelas */
    .stTable { 
        background-color: #FFFFFF !important; 
        border: 1px solid #002D5E; 
    }
    </style>
    """, unsafe_allow_html=True)

# 2. GESTÃO DE DADOS (COM TRAVA DE SEGURANÇA MÁXIMA)
DB_V = "logistica_aura_v20_viagens.csv"
DB_P = "logistica_aura_v20_passageiros.csv"

def carregar_dados():
    # Cria os arquivos se não existirem
    if not os.path.exists(DB_V):
        pd.DataFrame(columns=["Data", "Motorista", "Passageiro", "CC", "Saida", "Voo", "Trajeto", "Hospedagem", "Observacao", "Hotel_RS", "Aereo_RS", "Combust_RS", "Total_RS"]).to_csv(DB_V, index=False)
    if not os.path.exists(DB_P):
        pd.DataFrame(columns=["Nome", "CC_Padrao"]).to_csv(DB_P, index=False)
    
    try:
        v = pd.read_csv(DB_V).fillna("")
        p = pd.read_csv(DB_P).fillna("")
        return v, p
    except:
        # Se der qualquer erro na leitura, retorna DataFrames vazios com colunas corretas
        return pd.DataFrame(columns=["Data", "Motorista", "Passageiro", "CC", "Saida", "Voo", "Trajeto", "Hospedagem", "Observacao", "Hotel_RS", "Aereo_RS", "Combust_RS", "Total_RS"]), pd.DataFrame(columns=["Nome", "CC_Padrao"])

df_v, df_p = carregar_dados()

LISTA_CC = sorted([
    "210301 - Moagem", "210403 - Detox", "210801 - Laboratório", "211002 - Manut. Mecânica",
    "210405 - Lixiviação", "210101 - Admin. Planta", "320101 - Suprimentos", "320301 - RH"
])

# 3. SIDEBAR (LOGO E MENU)
with st.sidebar:
    # Logo com sombra e link estável
    st.markdown(f"""
        <div style="text-align: center;">
            <img src="https://gist.githubusercontent.com/user-attachments/assets/8e0f5228-40b9-4674-9f0f-6df3d57b280c" 
                 width="180" class="logo-aura">
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    menu = st.radio(
        "PAINEL DE CONTROLE",
        ["📋 Agenda Motoristas", "📝 Programar Vi
