import streamlit as st
import pandas as pd
from datetime import datetime

# 1. SETUP VISUAL INSTITUCIONAL (AZUL MARINHO #002D5E)
st.set_page_config(page_title="Aura Minerals - Logística", layout="wide")

st.markdown("""
    <style>
    /* Forçar Fundo Branco e Menu Azul */
    .stApp { background-color: #FFFFFF !important; }
    [data-testid="stSidebar"] { background-color: #002D5E !important; border-right: 2px solid #FFC20E; }
    [data-testid="stSidebar"] * { color: #FFFFFF !important; }
    
    /* Efeito Glow na Logo solicitado anteriormente */
    .logo-aura {
        filter: drop-shadow(0px 0px 10px rgba(255, 255, 255, 0.4));
        display: block; margin: auto; padding-bottom: 20px;
    }
    
    /* Feedback de Mensagens (Sucesso/Erro) */
    .stAlert { border-radius: 8px; font-weight: bold; }
    
    /* Títulos e Inputs */
    h1, h2, h3, label { color: #002D5E !important; font-family: 'Arial', sans-serif; }
    .stButton>button {
        background-color: #002D5E; color: white; border: 1px solid #FFC20E;
        width: 100%; font-weight: bold; height: 3em;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. MOTOR DE DADOS (SESSION STATE PARA PERSISTÊNCIA NA SESSÃO)
if 'viagens' not in st.session_state:
    st.session_state.viagens = pd.DataFrame(columns=[
        "Data", "Motorista", "Passageiro", "CC", "Saída", "Voo", "Trajeto", "Hospedagem", "Observação"
    ])

if 'funcionarios' not in st.session_state:
    st.session_state.funcionarios = pd.DataFrame(columns=["Nome", "Setor"])

# Centros de Custo Oficiais
LISTA_CC = sorted(["210301 - Moagem", "210403 - Detox", "210801 - Laboratório", "211002 - Manut. Mecânica", "320101 - Suprimentos", "320301 - RH", "310501 - Meio Ambiente"])

# 3. BARRA LATERAL
with st.sidebar:
    st.markdown("""
        <div style="text-align: center;">
            <img src="https://gist.githubusercontent.com/user-attachments/assets/8e0f5228-40b9-4674-9f0f-6df3d57b280c" 
                 width="180" class="logo-aura">
        </div>
        """, unsafe_allow_html=True)
    st.markdown("---")
    menu = st.radio("MÓDULOS DO SISTEMA", ["📋 Painel de Agenda", "📝 Programar Viagem", "👤 Gestão de Funcionários", "💰 Controle Financeiro"])
    st.markdown("---")
    st.caption("Aura Minerals | Unidade Apoena")

# 4. EXECUÇÃO DOS MÓDULOS

# --- MÓDULO: AGENDA ---
if menu == "📋 Painel de Agenda":
    st.header("📋 Agenda de Viagens Ativas")
    if not st.session_state.viagens.empty:
        st.table(st.session_state.viagens)
    else:
        st.info("ℹ️ Nenhuma viagem programada no momento.")

# --- MÓDULO: PROGRAMAÇÃO ---
elif menu == "📝 Programar Viagem":
    st.header("📝 Nova Programação de Transporte")
    
    if st.session_state.funcionarios.empty:
        st.error("❌ ERRO: Não há funcionários cadastrados. Acesse 'Gestão de Funcionários'.")
    else:
        with st.form("form_viagem", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            p_sel = col1.selectbox("Passageiro (Obrigatório)", st.session_state.funcionarios["Nome"].tolist())
            mot_v = col1.selectbox("Motorista Designado", ["Ilson", "Antonio"])
            data_v = col1.date_input("Data da Viagem", datetime.now())
            
            saida_v = col2.text_input("Horário de Saída (Ex: 07:30)")
            voo_v = col2.text_input("Informação de Voo (Se houver)")
            hosp_v = col2.text_input("Hospedagem / Destino Final")
            
            st.write("---")
            traj_v = st.selectbox("Trajeto Sugerido", ["P. LACERDA X CUIABÁ", "CUIABÁ X P. LACERDA", "INTERNO", "OUTRO"])
            cc_v = st.selectbox("Centro de Custo para Rateio", LISTA_CC)
            obs_v = st.text_area("Observações Importantes para o Motorista")
            
            if st.form_submit_button("CONFIRMAR E SALVAR PROGRAMAÇÃO"):
                if not saida_v:
                    st.warning("⚠️ O campo 'Horário de Saída' é obrigatório para o motorista.")
                else:
                    nova_v = pd.DataFrame([{
                        "Data": data_v.strftime('%d/%m/%Y'), "Motorista": mot_v, "Passageiro": p_sel, 
                        "CC": cc_v, "Saída": saida_v, "Voo": voo_v, "
