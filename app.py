import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 1. IDENTIDADE VISUAL RIGOROSA (STYLEGUIDE AURA APOENA)
st.set_page_config(
    page_title="Logística Aura Minerals Apoena",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS para forçar Fundo Branco e o Azul Marinho institucional
st.markdown("""
    <style>
    /* Forçar Fundo Branco */
    .stApp { background-color: #FFFFFF !important; }
    
    /* Barra Lateral - Azul Marinho Aura */
    [data-testid="stSidebar"] {
        background-color: #002D5E !important; 
        border-right: 2px solid #FFC20E; /* Linha Ocre Aura */
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
    
    /* Títulos em Azul Marinho */
    h1, h2, h3, h4, p, span, label { 
        color: #002D5E !important; 
        font-family: 'Arial', sans-serif !important; 
    }
    
    /* Botões Padrão Aura */
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
    
    /* Tabelas */
    .stTable { 
        background-color: #FFFFFF !important; 
        color: #002D5E !important; 
        border: 1px solid #002D5E; 
    }
    </style>
    """, unsafe_allow_html=True)

# 2. GESTÃO DE DADOS (VERSÃO V23 - SEGURANÇA MÁXIMA)
DB_V = "logistica_aura_v23_viagens.csv"
DB_P = "logistica_aura_v23_passageiros.csv"

def carregar_dados():
    cols_v = ["Data", "Motorista", "Passageiro", "CC", "Saida", "Voo", "Trajeto", "Hospedagem", "Observacao", "Hotel_RS", "Aereo_RS", "Combust_RS", "Total_RS"]
    cols_p = ["Nome", "CC_Padrao"]
    if not os.path.exists(DB_V): pd.DataFrame(columns=cols_v).to_csv(DB_V, index=False)
    if not os.path.exists(DB_P): pd.DataFrame(columns=cols_p).to_csv(DB_P, index=False)
    try:
        v = pd.read_csv(DB_V).fillna("")
        p = pd.read_csv(DB_P).fillna("")
        return v, p
    except:
        return pd.DataFrame(columns=cols_v), pd.DataFrame(columns=cols_p)

df_v, df_p = carregar_dados()

LISTA_CC = sorted(["210301 - Moagem", "210403 - Detox", "210801 - Laboratório", "211002 - Manut. Mecânica", "320101 - Suprimentos", "320301 - RH"])

# 3. SIDEBAR COM LOGO (LINK DIRETO ESTÁVEL)
with st.sidebar:
    # Usei o link que funcionou anteriormente para garantir a visualização
    st.markdown(f"""
        <div style="text-align: center;">
            <img src="https://gist.githubusercontent.com/user-attachments/assets/8e0f5228-40b9-4674-9f0f-6df3d57b280c" 
                 width="190" class="logo-aura">
        </div>
        """, unsafe_allow_html=True)
    st.markdown("---")
    menu = st.radio("NAVEGAÇÃO", ["📋 Agenda Motoristas", "📝 Programar Viagem", "👤 Cadastrar Viajante", "💰 Financeiro"])

# 4. MÓDULOS
if menu == "📋 Agenda Motoristas":
    st.header("Agenda Operacional")
    if not df_v.empty:
        st.table(df_v[["Data", "Motorista", "Passageiro", "Saida", "Voo", "Trajeto", "Hospedagem", "Observacao"]])
    else: st.info("Nenhuma programação.")

elif menu == "📝 Programar Viagem":
    st.header("Programação")
    if df_p.empty:
        st.warning("⚠️ Cadastre o viajante primeiro.")
    else:
        nomes = sorted(df_p["Nome"].tolist())
        p_sel = st.selectbox("Escolha o Passageiro", nomes)
        with st.form("form_v23"):
            c1, c2 = st.columns(2)
            dt = c1.date_input("Data", datetime.now())
            mot = c1.selectbox("Motorista", ["Ilson", "Antonio"])
            sd = c1.text_input("Saída")
            voo = c2.text_input("Voo")
            hosp = c2.text_input("Destino")
            obs = st.text_area("Observações")
            if st.form_submit_button("✅ SALVAR"):
                nova = pd.DataFrame([{"Data": dt.strftime('%d/%m/%Y'), "Motorista": mot, "Passageiro": p_sel, "CC": "Rateio", "Saida": sd, "Voo": voo, "Trajeto": "-", "Hospedagem": hosp, "Observacao": obs, "Hotel_RS": 0.0, "Aereo_RS": 0.0, "Combust_RS": 0.0, "Total_RS": 0.0}])
                pd.concat([df_v, nova], ignore_index=True).to_csv(DB_V, index=False)
                st.success("Salvo!")
                st.rerun()

elif menu == "👤 Cadastrar Viajante":
    st.header("Cadastro")
    with st.form("cad_v23"):
        n = st.text_input("Nome").upper()
        if st.form_submit_button("CADASTRAR"):
            if n:
                pd.concat([df_p, pd.DataFrame([{"Nome": n, "CC_Padrao": "Geral"}])], ignore_index=True).to_csv(DB_P, index=False)
                st.success(f"{n} cadastrado!")
                st.rerun()

elif menu == "💰 Financeiro":
    st.header("Financeiro")
    if not df_v.empty:
        df_ed = st.data_editor(df_v)
        if st.button("Salvar"):
            df_ed.to_csv(DB_V, index=False)
            st.success("Dados Atualizados!")
