import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 1. SETUP VISUAL (AJUSTE FINAL DA BORDA)
st.set_page_config(page_title="Logística Aura Minerals", layout="wide")

st.markdown("""
    <style>
    /* Fundo Geral Branco */
    .stApp { background-color: #FFFFFF !important; }
    
    /* Barra Lateral Azul Aura - LINHA AMARELA REMOVIDA AQUI */
    [data-testid="stSidebar"] {
        background-color: #002D5E !important;
        border-right: 2px solid #002D5E !important; /* Ficou azul para sumir a linha */
    }
    [data-testid="stSidebar"] * { color: #FFFFFF !important; }
    
    /* Logo com Sombra */
    .logo-aura {
        filter: drop-shadow(0px 4px 10px rgba(255, 255, 255, 0.4));
        display: block; margin: auto; padding-bottom: 20px;
    }
    
    /* FONTES GERAIS E RÓTULOS EM AZUL MARINHO */
    h1, h2, h3, h4, p, span, label, div, small { 
        color: #002D5E !important; 
    }
    
    /* --- CAMPOS CINZAS COM LETRA PRETA --- */
    input, select, textarea, div[data-baseweb="input"], div[data-baseweb="select"] > div {
        background-color: #E8E8E8 !important; 
        color: #000000 !important; 
    }
    
    /* Texto digitado sempre preto */
    input { color: #000000 !important; }
    textarea { color: #000000 !important; }
    div[role="listbox"] { color: #000000 !important; }

    /* Botões: Azul com Letra Branca */
    .stButton>button {
        background-color: #002D5E !important; 
        color: #FFFFFF !important;
        border: 2px solid #FFC20E !important; 
        border-radius: 5px;
        font-weight: bold; 
        width: 100%;
    }
    
    /* Financeiro com fundo cinza */
    [data-testid="stDataEditor"] {
        background-color: #E8E8E8 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. BANCO DE DADOS (LÓGICA INALTERADA)
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

# 3. BARRA LATERAL
with st.sidebar:
    st.markdown("""<div style="text-align: center;"><img src="https://gist.githubusercontent.com/user-attachments/assets/8e0f5228-40b9-4674-9f0f-6df3d57b280c" width="180" class="logo-aura"></div>""", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown(f"👥 **Funcionários:** {len(df_p)}")
    st.markdown(f"🚛 **Total de Viagens:** {len(df_v)}")
    st.markdown("---")
    menu = st.radio("NAVEGAÇÃO", ["📋 Agenda Motoristas", "📝 Programar Viagem", "👤 Cadastrar Viajante", "💰 Financeiro"])

# 4. MÓDULOS
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
            traj_v = st.selectbox("Trajeto", ["P. LACERDA X CUIABÁ", "CUIABÁ X P. LACERDA", "INTERNO", "OUTRO"])
            obs_v = st.text_area("Observação")
            if st.form_submit_button("✅ SALVAR PROGRAMAÇÃO"):
                nova = pd.DataFrame([{"Data": data_v.strftime('%d/%m/%Y'), "Motorista": mot_v, "Passageiro": p_sel, "Saida": saida_v, "Voo": voo_v, "Trajeto": traj_v, "Hospedagem": hosp_v, "Observacao": obs_v}])
                pd.concat([df_v, nova], ignore_index=True).to_csv(DB_V, index=False)
                st.success("Salvo!")
                st.rerun()

elif menu == "👤 Cadastrar Viajante":
    st.header("👤 Cadastro")
    with st.form("cad"):
        n = st.text_input("Nome").upper()
        if st.form_submit_button("CADASTRAR FUNCIONÁRIO"):
            if n:
                pd.concat([df_p, pd.DataFrame([{"Nome": n}])], ignore_index=True).to_csv(DB_P, index=False)
                st.success(f"✅ {n} cadastrado!")
                st.rerun()
    st.dataframe(df_p)

elif menu == "💰 Financeiro":
    st.header("💰 Controle Financeiro")
    df_editado = st.data_editor(df_v, use_container_width=True, num_rows="dynamic")
    if st.button("💾 SALVAR ALTERAÇÕES"):
        df_editado.to_csv(DB_V, index=False)
        st.success("✅ Financeiro Atualizado!")
