import streamlit as st
import pandas as pd
from datetime import datetime

# 1. SETUP VISUAL (AZUL MARINHO, OCRE E BRANCO)
st.set_page_config(page_title="Aura Minerals - Logística Apoena", layout="wide")

st.markdown("""
    <style>
    /* Forçar Fundo Branco */
    .stApp { background-color: #FFFFFF !important; }
    
    /* Barra Lateral - Azul Marinho Aura */
    [data-testid="stSidebar"] {
        background-color: #002D5E !important;
        border-right: 3px solid #FFC20E;
    }
    [data-testid="stSidebar"] * { color: #FFFFFF !important; }
    
    /* SOMBRA NA LOGO (GLOW) */
    .logo-aura {
        filter: drop-shadow(0px 0px 10px rgba(255, 255, 255, 0.4));
        display: block; margin: auto; padding-bottom: 20px;
    }
    
    /* Cores dos Textos */
    h1, h2, h3, h4, label { color: #002D5E !important; font-family: 'Arial', sans-serif; }
    
    /* Botões */
    .stButton>button {
        background-color: #002D5E; color: white;
        border: 1px solid #FFC20E; font-weight: bold;
    }
    .stTable { background-color: white !important; border: 1px solid #002D5E; }
    </style>
    """, unsafe_allow_html=True)

# 2. INICIALIZAÇÃO DA MEMÓRIA (TODOS OS CAMPOS RESTAURADOS)
if 'db_viagens' not in st.session_state:
    st.session_state.db_viagens = pd.DataFrame(columns=[
        "Data", "Motorista", "Passageiro", "Saida", "Voo", "Trajeto", "Hospedagem", "Observacao"
    ])

if 'db_passageiros' not in st.session_state:
    st.session_state.db_passageiros = pd.DataFrame(columns=["Nome"])

# 3. BARRA LATERAL (LOGO E NAVEGAÇÃO)
with st.sidebar:
    # Logo com sombra
    st.markdown("""
        <div style="text-align: center;">
            <img src="https://gist.githubusercontent.com/user-attachments/assets/8e0f5228-40b9-4674-9f0f-6df3d57b280c" 
                 width="180" class="logo-aura">
        </div>
        """, unsafe_allow_html=True)
    st.markdown("---")
    menu = st.radio("NAVEGAÇÃO", ["📋 Agenda Motoristas", "📝 Programar Viagem", "👤 Cadastrar Viajante", "💰 Financeiro"])

# 4. MÓDULOS

if menu == "📋 Agenda Motoristas":
    st.header("📋 Agenda de Viagens Operacionais")
    if not st.session_state.db_viagens.empty:
        st.table(st.session_state.db_viagens)
    else:
        st.info("Nenhuma viagem programada.")

elif menu == "📝 Programar Viagem":
    st.header("📝 Programar Nova Viagem")
    if st.session_state.db_passageiros.empty:
        st.warning("⚠️ Vá em 'Cadastrar Viajante' e adicione um nome primeiro.")
    else:
        # FORMULÁRIO COM TODOS OS CAMPOS QUE VOCÊ TINHA ANTES
        with st.form("form_completo", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            p_sel = col1.selectbox("Passageiro", st.session_state.db_passageiros["Nome"].tolist())
            mot_v = col1.selectbox("Motorista", ["Ilson", "Antonio"])
            data_v = col1.date_input("Data da Viagem", datetime.now())
            
            saida_v = col2.text_input("Horário de Saída")
            voo_v = col2.text_input("Voo / Horário de Chegada")
            hosp_v = col2.text_input("Hotel / Destino Final")
            
            st.write("---")
            traj_v = st.selectbox("Trajeto", ["P. LACERDA X CUIABÁ", "CUIABÁ X P. LACERDA", "INTERNO", "OUTRO"])
            obs_v = st.text_area("Observações para o Motorista")
            
            if st.form_submit_button("✅ SALVAR PROGRAMAÇÃO"):
                nova_v = pd.DataFrame([{
                    "Data": data_v.strftime('%d/%m/%Y'), 
                    "Motorista": mot_v, 
                    "Passageiro": p_sel, 
                    "Saida": saida_v, 
                    "Voo": voo_v, 
                    "Trajeto": traj_v, 
                    "Hospedagem": hosp_v, 
                    "Observacao": obs_v
                }])
                st.session_state.db_viagens = pd.concat([st.session_state.db_viagens, nova_v], ignore_index=True)
                st.success("Viagem salva com sucesso!")
                st.rerun()

elif menu == "👤 Cadastrar Viajante":
    st.header("👤 Cadastro de Funcionário")
    with st.form("cad_f"):
        n_novo = st.text_input("Nome Completo").upper()
        if st.form_submit_button("CADASTRAR"):
            if n_novo:
                novo_df = pd.DataFrame([{"Nome": n_novo}])
                st.session_state.db_passageiros = pd.concat([st.session_state.db_passageiros, novo_df], ignore_index=True)
                st.success(f"{n_novo} cadastrado!")
                st.rerun()

elif menu == "💰 Financeiro":
    st.header("💰 Controle Financeiro")
    # Permite editar a tabela de viagens diretamente
    st.session_state.db_viagens = st.data_editor(st.session_state.db_viagens)
