import streamlit as st
import pandas as pd
from datetime import datetime
import time

# 1. SETUP VISUAL DE ALTO NÍVEL (STYLEGUIDE AURA)
st.set_page_config(
    page_title="ERP Logística | Aura Minerals",
    page_icon="🚛",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização CSS Avançada
st.markdown("""
    <style>
    /* Forçar Fundo Branco e Menu Azul Marinho (#002D5E) */
    .stApp { background-color: #FFFFFF !important; }
    [data-testid="stSidebar"] {
        background-color: #002D5E !important;
        border-right: 3px solid #FFC20E; /* Ocre Aura */
    }
    [data-testid="stSidebar"] * { color: #FFFFFF !important; }
    
    /* Glow/Sombra na Logo Marca */
    .logo-container { text-align: center; padding: 10px; }
    .logo-aura {
        filter: drop-shadow(0px 4px 12px rgba(255, 255, 255, 0.4));
        margin-bottom: 20px;
    }
    
    /* Padronização de Mensagens de Sistema */
    .stAlert { border: 1px solid #002D5E; border-radius: 10px; }
    
    /* Botões Corporativos */
    .stButton>button {
        background-color: #002D5E; color: white;
        border: 1px solid #FFC20E; border-radius: 5px;
        font-weight: bold; width: 100%; transition: 0.3s;
    }
    .stButton>button:hover { background-color: #FFC20E; color: #002D5E; }
    
    /* Estilo de Tabelas (Zebra e Bordas) */
    .stTable { border: 1px solid #002D5E; border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

# 2. MOTOR DE PERSISTÊNCIA (SESSION STATE)
# Definindo as estruturas de dados como tabelas reais de banco de dados
if 'db_viagens' not in st.session_state:
    st.session_state.db_viagens = pd.DataFrame(columns=[
        "ID", "Data_Ref", "Motorista", "Passageiro", "CC_Rateio", 
        "H_Saida", "Voo_Info", "Trajeto_F", "Local_Hosp", "Observacoes_Op"
    ])

if 'db_cadastro' not in st.session_state:
    st.session_state.db_cadastro = pd.DataFrame(columns=["Nome_Completo", "Setor_Responsavel", "CC_Fixo"])

# Centros de Custo (Mapa Oficial Aura)
LISTA_CC = sorted([
    "210301 - Moagem", "210403 - Detox", "210801 - Laboratório", 
    "211002 - Manut. Mecânica", "320101 - Suprimentos", "320301 - RH", 
    "310501 - Meio Ambiente", "121101 - Geologia", "121001 - Planejamento"
])

# 3. BARRA LATERAL (IDENTIDADE E CONTROLE)
with st.sidebar:
    st.markdown('<div class="logo-container">', unsafe_allow_html=True)
    # Logo com Sombra (Glow)
    st.markdown(f'<img src="https://gist.githubusercontent.com/user-attachments/assets/8e0f5228-40b9-4674-9f0f-6df3d57b280c" width="190" class="logo-aura">', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    menu = st.radio("MÓDULOS DE GESTÃO", [
        "📊 Dashboard de Agenda", 
        "📋 Programar Nova Viagem", 
        "👥 Cadastro de Funcionários", 
        "💸 Controle de Custos (Financeiro)"
    ])
    st.markdown("---")
    st.info(f"**Status:** Sistema Online\n**Unidade:** Apoena\n**Data:** {datetime.now().strftime('%d/%m/%Y')}")

# 4. DESENVOLVIMENTO DOS MÓDULOS DETALHADOS

# --- MÓDULO: DASHBOARD ---
if menu == "📊 Dashboard de Agenda":
    st.subheader("📊 Agenda Operacional de Transportes")
    if not st.session_state.db_viagens.empty:
        # Exibição Profissional
        st.dataframe(st.session_state.db_viagens, use_container_width=True, hide_index=True)
        
        # Opção de Download para o Motorista
        csv = st.session_state.db_viagens.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 Baixar Agenda para Motorista (Excel/CSV)", csv, "agenda_viagens_aura.csv")
    else:
        st.warning("⚠️ O banco de dados de viagens está vazio. Inicie uma programação.")

# --- MÓDULO: PROGRAMAÇÃO ---
elif menu == "📋 Programar Nova Viagem":
    st.subheader("📋 Formulário de Programação de Viagem")
    
    if st.session_state.db_cadastro.empty:
        st.error("❌ AÇÃO NECESSÁRIA: Não há passageiros cadastrados. Realize o cadastro antes de programar.")
    else:
        with st.form("form_viagem_detalhado", clear_on_submit=True):
            col1, col2, col3 = st.columns(3)
            
            p_sel = col1.selectbox("Passageiro*", sorted(st.session_state.db_cadastro["Nome_Completo"].tolist()))
            mot_v = col1.selectbox("Motorista*", ["Ilson", "Antonio"])
            dt_v = col1.date_input("Data da Viagem", datetime.now())
            
            h_saida = col2.text_input("Horário de Saída
