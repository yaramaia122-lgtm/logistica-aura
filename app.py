import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 1. IDENTIDADE VISUAL (AURA MINERALS)
st.set_page_config(
    page_title="Logística Aura Apoena",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS para forçar fundo branco e a sombra na logo marca
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF !important; }
    [data-testid="stSidebar"] {
        background-color: #002D5E !important; 
        border-right: 2px solid #FFC20E;
    }
    [data-testid="stSidebar"] * { color: #FFFFFF !important; }
    
    /* EFEITO DE SOMBRA NA LOGO */
    .logo-aura {
        filter: drop-shadow(0px 0px 10px rgba(255, 255, 255, 0.4));
        margin-bottom: 20px;
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
    
    .stTable { background-color: #FFFFFF !important; border: 1px solid #002D5E; }
    </style>
    """, unsafe_allow_html=True)

# 2. GESTÃO DE DADOS COM SEGURANÇA (TRAVA ANTI-ERRO)
DB_V = "logistica_aura_v21_viagens.csv"
DB_P = "logistica_aura_v21_passageiros.csv"

def carregar_dados():
    # Garante que as colunas existam mesmo se o arquivo for novo
    cols_v = ["Data", "Motorista", "Passageiro", "CC", "Saida", "Voo", "Trajeto", "Hospedagem", "Observacao", "Hotel_RS", "Aereo_RS", "Combust_RS", "Total_RS"]
    cols_p = ["Nome", "CC_Padrao"]
    
    if not os.path.exists(DB_V): pd.DataFrame(columns=cols_v).to_csv(DB_V, index=False)
    if not os.path.exists(DB_P): pd.DataFrame(columns=cols_p).to_csv(DB_P, index=False)
    
    try:
        # Tenta ler, mas se o arquivo estiver vazio, cria um DataFrame com as colunas certas
        v = pd.read_csv(DB_V)
        if v.empty: v = pd.DataFrame(columns=cols_v)
        p = pd.read_csv(DB_P)
        if p.empty: p = pd.DataFrame(columns=cols_p)
        return v.fillna(""), p.fillna("")
    except:
        return pd.DataFrame(columns=cols_v), pd.DataFrame(columns=cols_p)

df_v, df_p = carregar_dados()

LISTA_CC = sorted(["210301 - Moagem", "210403 - Detox", "210801 - Laboratório", "211002 - Manut. Mecânica", "320101 - Suprimentos", "320301 - RH"])

# 3. SIDEBAR
with st.sidebar:
    # Link direto para a logo com a sombra aplicada
    st.markdown(f"""
        <div style="text-align: center;">
            <img src="https://gist.githubusercontent.com/user-attachments/assets/8e0f5228-40b9-4674-9f0f-6df3d57b280c" 
                 width="180" class="logo-aura">
        </div>
        """, unsafe_allow_html=True)
    st.markdown("---")
    menu = st.radio("NAVEGAÇÃO", ["📋 Agenda Motoristas", "📝 Programar Viagem", "👤 Cadastrar Viajante", "💰 Financeiro"])

# 4. MÓDULOS

if menu == "📋 Agenda Motoristas":
    st.header("Agenda Operacional")
    if not df_v.empty:
        st.table(df_v[["Data", "Motorista", "Passageiro", "Saida", "Voo", "Trajeto", "Hospedagem", "Observacao"]])
    else:
        st.info("Nenhuma programação. Cadastre uma viagem para começar.")

elif menu == "📝 Programar Viagem":
    st.header("Programação")
    if df_p.empty:
        st.warning("⚠️ Cadastre um viajante primeiro no menu ao lado.")
    else:
        nomes = sorted(df_p["Nome"].tolist())
        p_sel = st.selectbox("Passageiro", nomes)
        
        with st.form("form_v21", clear_on_submit=True):
            c1, c2 = st.columns(2)
            dt = c1.date_input("Data", datetime.now())
            mot = c1.selectbox("Motorista", ["Ilson", "Antonio"])
            sd = c1.text_input("Horário Saída")
            voo = c2.text_input("Voo / Horário")
            hosp = c2.text_input("Hotel / Destino")
            obs = st.text_area("Observações")
            
            if st.form_submit_button("✅ SALVAR"):
                nova = pd.DataFrame([{"Data": dt.strftime('%d/%m/%Y'), "Motorista": mot, "Passageiro": p_sel, "CC": "Rateio", "Saida": sd, "Voo": voo, "Trajeto": "-", "Hospedagem": hosp, "Observacao": obs, "Hotel_RS": 0.0, "Aereo_RS": 0.0, "Combust_RS": 0.0, "Total_RS": 0.0}])
                pd.concat([df_v, nova], ignore_index=True).to_csv(DB_V, index=False)
                st.success("Salvo!")
                st.rerun()

elif menu == "👤 Cadastrar Viajante":
    st.header("Cadastro")
    with st.form("cad_v21"):
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
        if st.button("Salvar Financeiro"):
            df_ed.to_csv(DB_V, index=False)
            st.success("Dados Atualizados!")
