import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 1. SETUP VISUAL (AZUL MARINHO EM TUDO)
st.set_page_config(page_title="Logística Aura Minerals", layout="wide")

st.markdown("""
    <style>
    /* Fundo Branco */
    .stApp { background-color: #FFFFFF !important; }
    
    /* Barra Lateral Azul Aura */
    [data-testid="stSidebar"] {
        background-color: #002D5E !important;
        border-right: 3px solid #FFC20E;
    }
    [data-testid="stSidebar"] * { color: #FFFFFF !important; }
    
    /* Sombra na Logo */
    .logo-aura {
        filter: drop-shadow(0px 4px 10px rgba(255, 255, 255, 0.4));
        display: block; margin: auto; padding-bottom: 20px;
    }
    
    /* AZUL MARINHO EM TODAS AS FONTES (Grandes e Pequenas) */
    h1, h2, h3, h4, p, span, label, div, small, .stMarkdown { 
        color: #002D5E !important; 
        font-family: 'Arial', sans-serif !important; 
    }
    
    /* Cor Azul específica para os rótulos de campos (letras menores) */
    .stTextInput label, .stSelectbox label, .stDateInput label, .stTextArea label, [data-testid="stHeader"] {
        color: #002D5E !important;
        font-weight: bold !important;
    }

    /* Botão Azul com Borda Ocre */
    .stButton>button {
        background-color: #002D5E; color: white !important;
        border: 2px solid #FFC20E; border-radius: 5px;
        font-weight: bold; width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. BANCO DE DADOS (Nomes fixos para não "limpar" as abas)
DB_V = "banco_viagens_oficial.csv"
DB_P = "banco_passageiros_oficial.csv"

def carregar_dados():
    cols_v = ["Data", "Motorista", "Passageiro", "CC", "Saida", "Voo", "Trajeto", "Hospedagem", "Observacao"]
    if not os.path.exists(DB_V): pd.DataFrame(columns=cols_v).to_csv(DB_V, index=False)
    if not os.path.exists(DB_P): pd.DataFrame(columns=["Nome", "Centro_Custo"]).to_csv(DB_P, index=False)
    
    v = pd.read_csv(DB_V).fillna("")
    p = pd.read_csv(DB_P).fillna("")
    return v, p

df_v, df_p = carregar_dados()

# 3. SIDEBAR
with st.sidebar:
    st.markdown("""<div style="text-align: center;"><img src="https://gist.githubusercontent.com/user-attachments/assets/8e0f5228-40b9-4674-9f0f-6df3d57b280c" width="180" class="logo-aura"></div>""", unsafe_allow_html=True)
    st.markdown("---")
    menu = st.radio("NAVEGAÇÃO", ["📋 Agenda Motoristas", "📝 Programar Viagem", "👤 Cadastrar Viajante", "💰 Financeiro"])

# 4. MÓDULOS

if menu == "📋 Agenda Motoristas":
    st.header("📋 Agenda Operacional")
    if not df_v.empty:
        st.dataframe(df_v, use_container_width=True, hide_index=True)
    else:
        st.write("Nenhuma viagem programada.")

elif menu == "📝 Programar Viagem":
    st.header("📝 Programar Viagem")
    if df_p.empty:
        st.error("⚠️ ABA EM BRANCO: Cadastre um viajante primeiro para habilitar esta função.")
    else:
        with st.form("form_viagem"):
            c1, c2 = st.columns(2)
            p_sel = c1.selectbox("Passageiro*", df_p["Nome"].tolist())
            mot_v = c1.selectbox("Motorista*", ["Ilson", "Antonio"])
            data_v = c1.date_input("Data", datetime.now())
            
            saida_v = c2.text_input("Saída*")
            voo_v = c2.text_input("Voo")
            hosp_v = c2.text_input("Hospedagem")
            
            traj_v = st.selectbox("Trajeto", ["P. LACERDA X CUIABÁ", "CUIABÁ X P. LACERDA", "INTERNO", "OUTRO"])
            obs_v = st.text_area("Observação")
            
            if st.form_submit_button("✅ SALVAR"):
                nova_v = pd.DataFrame([{"Data": data_v.strftime('%d/%m/%Y'), "Motorista": mot_v, "Passageiro": p_sel, "Saida": saida_v, "Voo": voo_v, "Trajeto": traj_v, "Hospedagem": hosp_v, "Observacao": obs_v}])
                pd.concat([df_v, nova_v], ignore_index=True).to_csv(DB_V, index=False)
                st.success("Salvo!")
                st.rerun()

elif menu == "👤 Cadastrar Viajante":
    st.header("👤 Cadastro")
    with st.form("cad"):
        n = st.text_input("Nome").upper()
        if st.form_submit_button("CADASTRAR"):
            if n:
                pd.concat([df_p, pd.DataFrame([{"Nome": n}])], ignore_index=True).to_csv(DB_P, index=False)
                st.success(f"{n} cadastrado!")
                st.rerun()
    st.dataframe(df_p, use_container_width=True)

elif menu == "💰 Financeiro":
    st.header("💰 Financeiro")
    if not df_v.empty:
        df_ed = st.data_editor(df_v)
        if st.button("Salvar"):
            df_ed.to_csv(DB_V, index=False)
            st.success("Atualizado!")
