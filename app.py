import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 1. IDENTIDADE VISUAL COMPLETA
st.set_page_config(page_title="Aura Minerals - Logística Apoena", layout="wide")

st.markdown("""
    <style>
    /* Bloqueio de Tema Escuro e Fixação de Fundo Branco */
    .stApp { background-color: #FFFFFF !important; }
    
    /* Barra Lateral Azul Marinho Aura */
    [data-testid="stSidebar"] {
        background-color: #002D5E !important;
        border-right: 2px solid #FFC20E;
    }
    [data-testid="stSidebar"] * { color: #FFFFFF !important; }
    
    /* EFEITO DE SOMBRA NA LOGO */
    .logo-aura {
        filter: drop-shadow(0px 0px 10px rgba(255, 255, 255, 0.4));
        display: block; margin: auto; padding-bottom: 20px;
    }
    
    /* Estilização de Textos e Botões */
    h1, h2, h3, h4, label { color: #002D5E !important; font-family: 'Arial', sans-serif; }
    
    .stButton>button {
        background-color: #002D5E; color: white;
        border: 1px solid #FFC20E; font-weight: bold;
        width: 100%;
    }
    .stButton>button:hover { background-color: #FFC20E; color: #002D5E; }
    
    /* Tabelas operacionais */
    .stTable { background-color: white !important; border: 1px solid #002D5E; }
    </style>
    """, unsafe_allow_html=True)

# 2. ESTRUTURA DE DADOS DETALHADA
DB_V = "logistica_viagens_v6.csv"
DB_P = "cadastro_passageiros_v6.csv"

# Definição de todas as colunas para facilitar a localização de erros
COLS_VIAGENS = [
    "Data", "Motorista", "Passageiro", "CC", "Saida", 
    "Voo", "Trajeto", "Hospedagem", "Observacao", 
    "Hotel_RS", "Aereo_RS", "Combustivel_RS", "Total_RS"
]

def carregar_sistema():
    if not os.path.exists(DB_V): 
        pd.DataFrame(columns=COLS_VIAGENS).to_csv(DB_V, index=False)
    if not os.path.exists(DB_P): 
        pd.DataFrame(columns=["Nome", "CC_Padrao"]).to_csv(DB_P, index=False)
    
    v = pd.read_csv(DB_V).fillna("")
    p = pd.read_csv(DB_P).fillna("")
    
    # Garantia de integridade das colunas
    for col in COLS_VIAGENS:
        if col not in v.columns: v[col] = ""
    return v, p

df_v, df_p = carregar_sistema()

LISTA_CC = sorted([
    "210301 - Moagem", "210403 - Detox", "210801 - Laboratório", "211002 - Manut. Mecânica",
    "210405 - Lixiviação planta", "210101 - Admin. planta", "211001 - Manut. Elétrica",
    "320101 - Suprimentos", "320301 - RH", "121101 - Geologia Ernesto", "121001 - Planejamento Mina",
    "310501 - Meio Ambiente", "310503 - Segurança Trabalho", "310502 - Saúde", "151101 - Geologia Nosde"
])

# 3. BARRA LATERAL (LOGO E MENU)
with st.sidebar:
    st.markdown("""
        <div style="text-align: center;">
            <img src="https://gist.githubusercontent.com/user-attachments/assets/8e0f5228-40b9-4674-9f0f-6df3d57b280c" 
                 width="180" class="logo-aura">
        </div>
        """, unsafe_allow_html=True)
    st.markdown("---")
    menu = st.radio("MÓDULOS", ["📋 Agenda Motoristas", "📝 Programar Viagem", "👤 Cadastrar Viajante", "💰 Financeiro"])
    st.markdown("---")
    st.caption("Aura Minerals Apoena | v26.0")

# 4. EXECUÇÃO DOS MÓDULOS

if menu == "📋 Agenda Motoristas":
    st.header("📋 Agenda de Viagens Operacionais")
    if not df_v.empty:
        # Exibição completa das colunas operacionais
        exibir = df_v[["Data", "Motorista", "Passageiro", "Saida", "Voo", "Trajeto", "Hospedagem", "Observacao"]]
        st.table(exibir)
        st.download_button("📥 Exportar para CSV", exibir.to_csv(index=False).encode('utf-8-sig'), "agenda_aura.csv")
    else:
        st.info("Nenhuma programação registrada.")

elif menu == "📝 Programar Viagem":
    st.header("📝 Nova Programação de Viagem")
    if df_p.empty:
        st.warning("⚠️ Cadastre um viajante primeiro no módulo correspondente.")
    else:
        with st.form("form_programacao_completo", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            # Seleção de Passageiro
            passag_sel = col1.selectbox("Passageiro", sorted(df_p["Nome"].tolist()))
            
            # Busca de CC Padrão (Lógica detalhada)
            cc_busca = df_p[df_p["Nome"] == passag_sel]["CC_Padrao"]
            cc_sugestao = cc_busca.iloc[0] if not cc_busca.empty else LISTA_CC[0]
            
            mot_v = col1.selectbox("Motorista", ["Ilson", "Antonio"])
            data_v = col1.date_input("Data da Viagem", datetime.now())
            
            # Dados de Voo e Saída
            saida_v = col2.text_input("Horário de Saída (Ex: 08:00)")
            voo_v = col2.text_input("Voo / Horário de Chegada")
            
            st.write("---")
            # Trajeto e Hospedagem
            traj_opcoes = ["P. LACERDA X
