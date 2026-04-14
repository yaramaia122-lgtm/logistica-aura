import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 1. SETUP VISUAL DE ALTA DISPONIBILIDADE
st.set_page_config(page_title="Aura Minerals | Logística Apoena", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF !important; }
    [data-testid="stSidebar"] {
        background-color: #002D5E !important;
        border-right: 3px solid #FFC20E;
    }
    [data-testid="stSidebar"] * { color: #FFFFFF !important; }
    .logo-aura {
        filter: drop-shadow(0px 4px 10px rgba(255, 255, 255, 0.4));
        display: block; margin: auto; padding-bottom: 20px;
    }
    h1, h2, h3, label { color: #002D5E !important; font-family: 'Arial Black', sans-serif; }
    .stButton>button {
        background-color: #002D5E; color: white;
        border: 2px solid #FFC20E; border-radius: 5px;
        font-weight: bold; height: 3em; width: 100%;
    }
    .stTable { background-color: white !important; border: 1px solid #002D5E; }
    </style>
    """, unsafe_allow_html=True)

# 2. ARQUITETURA DE DADOS (BANCO DE DADOS LOCAL CSV)
DB_V = "database_viagens_aura_v31.csv"
DB_P = "database_passageiros_aura_v31.csv"

def inicializar_banco():
    cols_v = ["ID", "Data", "Motorista", "Passageiro", "CC", "Saida", "Voo", "Trajeto", "Hospedagem", "Obs", "Status"]
    cols_p = ["Nome", "Centro_Custo", "Setor", "Data_Cadastro"]
    
    if not os.path.exists(DB_V): pd.DataFrame(columns=cols_v).to_csv(DB_V, index=False)
    if not os.path.exists(DB_P): pd.DataFrame(columns=cols_p).to_csv(DB_P, index=False)
    
    try:
        v = pd.read_csv(DB_V).fillna("")
        p = pd.read_csv(DB_P).fillna("")
        # Garantia de integridade de colunas
        for c in cols_v: 
            if c not in v.columns: v[c] = ""
        return v, p
    except:
        return pd.DataFrame(columns=cols_v), pd.DataFrame(columns=cols_p)

df_v, df_p = inicializar_banco()

# Centros de Custo Oficiais Aura
LISTA_CC = sorted(["210301 - Moagem", "210403 - Detox", "210801 - Laboratório", "211002 - Manut. Mecânica", "320101 - Suprimentos", "320301 - RH", "310501 - Meio Ambiente"])

# 3. SIDEBAR (CONTROLE DE STATUS)
with st.sidebar:
    st.markdown("""<div style="text-align: center;"><img src="https://gist.githubusercontent.com/user-attachments/assets/8e0f5228-40b9-4674-9f0f-6df3d57b280c" width="180" class="logo-aura"></div>""", unsafe_allow_html=True)
    st.markdown("---")
    menu = st.radio("MÓDULOS CORPORATIVOS", ["📊 Dashboard / Agenda", "📝 Programação de Viagens", "👤 Gestão de Funcionários", "💰 Auditoria Financeira"])
    st.markdown("---")
    # Indicadores de Sistema (Status Detalhado)
    st.subheader("📈 Status do Sistema")
    st.write(f"👥 Passageiros Ativos: **{len(df_p)}**")
    st.write(f"🚛 Viagens Registradas: **{len(df_v)}**")
    st.caption(f"Último acesso: {datetime.now().strftime('%H:%M:%S')}")

# 4. PROCESSAMENTO DOS MÓDULOS

if menu == "📊 Dashboard / Agenda":
    st.header("📊 Painel de Controle de Logística")
    if not df_v.empty:
        # Filtro de busca detalhado
        busca = st.text_input("🔍 Pesquisar na Agenda (Nome, Data ou Motorista)")
        df_filtrado = df_v[df_v.apply(lambda row: busca.lower() in row.astype(str).str.lower().values, axis=1)]
        st.dataframe(df_filtrado, use_container_width=True, hide_index=True)
    else:
        st.info("Nenhuma programação encontrada no banco de dados.")

elif menu == "📝 Programação de Viagens":
    st.header("📝 Nova Programação Detalhada")
    if df_p.empty:
        st.error("❌ SISTEMA TRAVADO: Nenhum passageiro cadastrado para viagem.")
    else:
        with st.form("form_viagem_v31", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            p_sel = c1.selectbox("Passageiro (Base de Dados)", sorted(df_p["Nome"].tolist()))
            mot_v = c1.selectbox("Motorista", ["Ilson", "Antonio"])
            data_v = c1.date_input("Data", datetime.now())
            
            saida_v = c2.text_input("Horário de Saída*", placeholder="Ex: 06:45")
            voo_v = c2.text_input("Voo / Conexão", placeholder="Ex: AD4567")
            hosp_v = c2.text_input("Local de Hospedagem", placeholder="Ex: Hotel Tayamã")
            
            traj_v = c3.selectbox("Trajeto Padrão", ["P. LACERDA X CUIABÁ", "CUIABÁ X P. LACERDA", "INTERNO", "OUTRO"])
