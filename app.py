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

# CSS para aplicar as cores exatas e o efeito de sombra na logo
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF !important; }
    [data-testid="stSidebar"] {
        background-color: #002D5E !important; 
        border-right: 2px solid #FFC20E;
    }
    [data-testid="stSidebar"] * { color: #FFFFFF !important; }
    
    /* SOMBRA NA LOGO (GLOW) */
    .logo-aura {
        filter: drop-shadow(0px 0px 12px rgba(255, 255, 255, 0.4));
        margin-bottom: 25px;
        display: block;
        margin-left: auto;
        margin-right: auto;
    }
    
    h1, h2, h3, h4, label, p, span { 
        color: #002D5E !important; 
        font-family: 'Arial', sans-serif !important; 
    }
    
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
    
    .stTable { 
        background-color: #FFFFFF !important; 
        border: 1px solid #002D5E; 
    }
    </style>
    """, unsafe_allow_html=True)

# 2. GESTÃO DE DADOS (VERSÃO V19 - COM TRAVA DE SEGURANÇA)
DB_V = "logistica_aura_v19_viagens.csv"
DB_P = "logistica_aura_v19_passageiros.csv"

def carregar
