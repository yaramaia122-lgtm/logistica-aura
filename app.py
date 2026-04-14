import streamlit as st
import pandas as pd
import os
from datetime import datetime
import base64

# 1. IDENTIDADE VISUAL AURA MINERALS APOENA (RIGOROSO)
# Restaurando Fundo Branco (#FFFFFF) e Menu Lateral Azul Aura (#002D5E)
st.set_page_config(
    page_title="Aura Minerals - Logística",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização CSS para forçar o Fundo Branco e Cores Institucionais
st.markdown("""
    <style>
    /* Forçar Fundo Branco em toda a aplicação */
    .stApp { background-color: #FFFFFF !important; }
    
    /* Barra Lateral - Azul Aura Institucional */
    [data-testid="stSidebar"] {
        background-color: #002D5E !important; 
        border-right: 2px solid #FFC20E; /* Borda Ocre Aura */
    }
    [data-testid="stSidebar"] * { color: #FFFFFF !important; }
    
    /* EFEITO DE SOMBRA NA LOGO (DROP-SHADOW) */
    .logo-com-sombra {
        filter: drop-shadow(0px 4px 8px rgba(0, 0, 0, 0.6));
        transition: 0.3s;
    }
    .logo-com-sombra:hover {
        filter: drop-shadow(0px 6px 12px rgba(0, 0, 0, 0.8));
    }
    
    /* Títulos e Textos em Azul Aura para Fundo Branco */
    h1, h2, h3, h4, p, span, label { 
        color: #002D5E !important; 
        font-family: 'Arial', sans-serif !important; 
    }
    
    /* Botões Padrão - Azul Aura com Texto Branco */
    .stButton>button {
        background-color: #002D5E;
        color: #FFFFFF;
        border: 2px solid #FFC20E; 
        border-radius: 4px;
        font-weight: bold;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #FFC20E;
        color: #002D5E;
    }
    
    /* Botão de Download (Destaque Dourado/Ocre com texto Preto) */
    .stDownloadButton>button {
        background-color: #FFC20E !important;
        color: #000000 !important;
        font-weight: 800 !important;
        border: 2px solid #000000 !important;
    }
    
    /* Tabelas operacionais com alto contraste em Fundo Branco */
    .stTable, [data-testid="stDataFrame"] {
        background-color: #FFFFFF;
        border: 1px solid #002D5E;
        color: #002D5E !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. INTELIGÊNCIA DE DADOS (BANCO DE DADOS LOCAL - VERSÃO V15.0)
DB_VIAGENS = "logistica_aura_v15_viagens.csv"
DB_PASSAGEIROS = "logistica_aura_v15_passageiros.csv"

def carregar_bancos():
    if not os.path.exists(DB_VIAGENS):
        pd.DataFrame(columns=["Data", "Motorista", "Passageiro", "CC", "Saida", "Voo", "Trajeto", "Hospedagem", "Observacao", "Hotel_RS", "Aereo_RS", "Combust_RS", "Total_RS"]).to_csv(DB_VIAGENS, index=False)
    if not os.path.exists(DB_PASSAGEIROS):
        pd.DataFrame(columns=["Nome", "CC_Padrao"]).to_csv(DB_PASSAGEIROS, index=False)
    return pd.read_csv(DB_VIAGENS).fillna(""), pd.read_csv(DB_PASSAGEIROS).fillna("")

df_v, df_p = carregar_bancos()

# LISTA COMPLETA DE CENTROS DE CUSTO (STYLEGUIDE MAPA)
LISTA_CC = sorted([
    "210301 - Moagem", "210403 - Detox", "210801 - Laboratório", "211002 - Manut. Mecânica",
    "210405 - Lixiviação planta", "210101 - Admin. planta", "211001 - Manut. Elétrica",
    "320101 - Suprimentos", "320301 - RH", "121101 - Geologia Ernesto", "121001 - Planejamento Mina",
    "310501 - Meio Ambiente", "310503 - Segurança Trabalho", "310502 - Saúde", "151101 - Geologia Nosde"
])

# 3. SIDEBAR COM IDENTIDADE VISUAL E LOGO COM SOMBRA
with st.sidebar:
    # LINK OFICIAL DA LOGO QUE VOCÊ ENVIOU - AGORA COM EFEITO DE SOMBRA (drop-shadow)
    # A classe CSS 'logo-com-sombra' aplica o efeito definido no CSS acima
    st.markdown("""
        <div style="text-align: center;">
            <img src="https://gist.githubusercontent.com/user-attachments/assets/8e0f5228-40b9-4674-9f0f-6df3d57b280c" width="200" class="logo-com-sombra">
        </div>
        """, unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("<h3 style='color: #FFFFFF; text-align: center;'>LOGÍSTICA APOENA</h3>", unsafe_allow_html=True)
    opcao = st.radio(
        "Selecione o Módulo:",
        ["📅 Agenda Motoristas", "📝 Programar Viagem", "👤 Cadastrar Viajante", "💰 Financeiro"]
    )
    st.markdown("---")
    st.caption("Aura Minerals Apoena | v15.0")

# 4. MÓDULOS OPERACIONAIS

if opcao == "📅 Agenda Motoristas":
    st.header("Agenda Operacional de Viagens")
    if not df_v.empty:
        agenda = df_v[["Data", "Motorista", "Passageiro", "Saida", "Voo", "Trajeto", "Hospedagem", "Observacao"]]
        st.table(agenda)
        csv = agenda.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 Exportar Agenda (CSV)", csv, "agenda_motoristas.csv", "text/csv")
    else: st.info("Nenhuma viagem programada.")

elif opcao == "📝 Programar Viagem":
    st.header("📝 Nova Programação")
    if df_p.empty:
        st.warning("⚠️ Cadastre o viajante primeiro no módulo '👤 Cadastrar Viajante'.")
    else:
        # Busca passageiros e CC padrão de forma segura (previne ValueError)
        passag_lista = sorted(df_p["Nome"].tolist())
        p_sel = st.selectbox("Selecione o Passageiro", passag_lista)
        cc_row = df_p[df_p["Nome"] == p_sel]["CC_Padrao"]
        cc_sugerido = cc_row.iloc[0] if
