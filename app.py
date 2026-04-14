import streamlit as st
import pandas as pd
import os
import base64
from datetime import datetime

# 1. SETUP VISUAL (CONTRASTE TOTAL: CINZA E AZUL ESCURO)
st.set_page_config(page_title="Logística Aura Minerals", layout="wide")

# Função para converter imagem local para Base64
def get_base64_of_bin_file(bin_file):
    if os.path.exists(bin_file):
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    return None

st.markdown("""
    <style>
    /* Fundo Geral Branco */
    .stApp { background-color: #FFFFFF !important; }
    
    /* Barra Lateral - Azul Marinho Aura */
    [data-testid="stSidebar"] {
        background-color: #002D5E !important;
        border-right: none !important;
    }
    [data-testid="stSidebar"] * { color: #FFFFFF !important; }
    
    /* Logo com Sombra Preta */
    .logo-aura {
        filter: drop-shadow(0px 0px 10px rgba(0, 0, 0, 0.8));
        display: block; margin: auto; padding-bottom: 20px;
    }
    
    /* FONTES GERAIS EM AZUL MARINHO */
    h1, h2, h3, h4, p, span, label, div, small { 
        color: #002D5E !important; 
    }
    
    /* --- CORREÇÃO DEFINITIVA: CAMPOS CINZAS COM LETRA AZUL ESCURO --- */
    /* Alvo: Inputs de texto, selectbox, dateinput e textarea */
    .stTextInput input, .stSelectbox div[data-baseweb="select"], .stDateInput input, .stTextArea textarea, 
    div[data-baseweb="input"], div[data-baseweb="base-input"], textarea {
        background-color: #E8E8E8 !important; /* Cinza Claro */
        color: #002D5E !important; /* Letra Azul Escuro */
        border: 1px solid #002D5E !important;
    }

    /* Forçar a cor do texto digitado e selecionado */
    input, select, textarea, span[data-baseweb="select"] {
        color: #002D5E !important;
        -webkit-text-fill-color: #002D5E !important;
    }

    /* Botões: Azul Aura com Letra Branca */
    .stButton>button {
        background-color: #002D5E !important; 
        color: #FFFFFF !important;
        border: 2px solid #FFC20E !important; 
        border-radius: 5px;
        font-weight: bold; width: 100%;
    }
    
    /* Financeiro (Editor) */
    [data-testid="stDataEditor"] {
        background-color: #E8E8E8 !important;
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
        if c not in v.columns: v[c] = ""
    return v, p

df_v, df_p = carregar_dados()

# 3. BARRA LATERAL (LOGO E TOTAIS)
with st.sidebar:
    img_path = "Aura (Azul e Ocre).png"
    img_b64 = get_base64_of_bin_file(img_path)
    if img_b64:
        st.markdown(f'<div style="text-align: center;"><img src="data:image/png;base64,{img_b64}" width="180" class="logo-aura"></div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div style="text-align: center;"><img src="https://gist.githubusercontent.com/user-attachments/assets/8e0f5228-40b9-4674-9f0f-6df3d57b280c" width="180" class="logo-aura"></div>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown(f"👥 **Funcionários:** {len(df_p)}")
    st.markdown(f"🚛 **Total de Viagens:** {len(df_v)}")
    st.markdown("---")
    menu = st.radio("NAVEGAÇÃO", ["📋 Agenda Motoristas", "📝 Programar Viagem", "👤 Cadastrar Viajante", "💰 Financeiro"])

# 4. MÓDULOS (LÓGICA INALTERADA)
if menu == "📋 Agenda Motoristas":
    st.header("📋 Agenda Operacional")
    if not df_v.empty:
        st.table(df_v[["Data", "Motorista", "Passageiro", "Saida", "Voo", "Trajeto", "Hospedagem", "Observacao"]])
    else:
        st.write("Nenhuma viagem programada.")

elif menu == "📝 Programar Viagem":
    st.header("📝 Programar Viagem")
    if df_p.empty:
        st.error("⚠️ Cadastre um viajante primeiro.")
    else:
        with st.form("form_viagem"):
            c1, c2 = st.columns(2)
            p_sel = c1.selectbox("Passageiro*", df_p["Nome"].tolist())
            mot_v = c1.selectbox("Motorista*", ["Ilson", "Antonio"])
            data_v = c1.date_input("Data", datetime.now())
            saida_v = c2.text_input("Saída*")
            voo_v = c2.text_input("Voo")
            hosp_v = c2.text_input("Hospedagem")
            traj_v = st.selectbox("Trajeto", ["P. LAC
