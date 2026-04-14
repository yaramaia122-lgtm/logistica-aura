import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 1. SETUP VISUAL (CONTRASTE E PADRÃO CORPORATIVO)
st.set_page_config(page_title="Logística Aura Minerals", layout="wide")

st.markdown("""
    <style>
    /* Fundo Geral Branco */
    .stApp { background-color: #FFFFFF !important; }
    
    /* Barra Lateral Azul Aura */
    [data-testid="stSidebar"] {
        background-color: #002D5E !important;
        border-right: 3px solid #FFC20E;
    }
    [data-testid="stSidebar"] * { color: #FFFFFF !important; }
    
    /* Logo com Sombra */
    .logo-aura {
        filter: drop-shadow(0px 4px 10px rgba(255, 255, 255, 0.4));
        display: block; margin: auto; padding-bottom: 20px;
    }
    
    /* FONTES GERAIS EM AZUL MARINHO */
    h1, h2, h3, h4, p, span, label, div, small, .stMarkdown { 
        color: #002D5E !important; 
    }
    
    /* Rótulos dos campos em Azul e Negrito */
    .stTextInput label, .stSelectbox label, .stDateInput label, .stTextArea label {
        color: #002D5E !important;
        font-weight: bold !important;
    }

    /* --- ESTILO DOS CAMPOS DE PREENCHIMENTO EM TODOS OS MÓDULOS --- */
    /* Fundo Cinza e Letra Preta para Inputs, Selects e Textareas */
    input, select, textarea, div[data-baseweb="input"] > div, div[data-baseweb="select"] > div {
        background-color: #E8E8E8 !important; /* Cinza */
        color: #000000 !important; /* Letra Preta */
    }
    
    /* Garante cor preta no texto digitado */
    input { color: #000000 !important; }
    textarea { color: #000000 !important; }

    /* Botão Azul Aura - Padrão para todos os botões de Salvar/Cadastrar */
    .stButton>button {
        background-color: #002D5E; 
        color: #FFFFFF !important;
        border: 2px solid #FFC20E; 
        border-radius: 5px;
        font-weight: bold; 
        width: 100%;
        height: 3em;
    }
    .stButton>button:hover {
        background-color: #FFC20E; 
        color: #002D5E !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. BANCO DE DADOS (LÓGICA PRESERVADA)
DB_V = "banco_viagens_oficial.csv"
DB_P = "banco_passageiros_oficial.csv"

def carregar_dados():
    cols_v = ["Data", "Motorista", "Passageiro", "CC", "Saida", "Voo", "Trajeto", "Hospedagem", "Observacao", "Valor"]
    if not os.path.exists(DB_V): pd.DataFrame(columns=cols_v).to_csv(DB_V, index=False)
    if not os.path.exists(DB_P): pd.DataFrame(columns=["Nome", "CC_Padrao"]).to_csv(DB_P, index=False)
    v = pd.read_csv(DB_V).fillna("")
    p = pd.read_csv(DB_P).fillna("")
    for c in cols_v:
