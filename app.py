import streamlit as st
import pandas as pd
import os
from datetime import datetime
import base64

# 1. FORÇAR TEMA CLARO E CORES DA AURA (OCRE, BRANCO E PRETO)
st.set_page_config(page_title="Aura Minerals - Logística", layout="wide")

# CSS "Blindado" para garantir o fundo branco e visual profissional
st.markdown("""
    <style>
    /* Forçar Fundo Branco */
    .stApp { background-color: #FFFFFF !important; }
    
    /* Barra Lateral - Cor Ocre/Dourada da Aura */
    [data-testid="stSidebar"] {
        background-color: #FFC20E !important;
        border-right: 2px solid #000000;
    }
    [data-testid="stSidebar"] * { color: #000000 !important; font-weight: bold; }
    
    /* Textos em Preto para leitura fácil */
    h1, h2, h3, h4, label, p, span { 
        color: #000000 !important; 
        font-family: 'Arial', sans-serif !important; 
    }
    
    /* Botões Pretos com texto Dourado */
    .stButton>button {
        background-color: #000000;
        color: #FFC20E;
        border: 2px solid #000000;
        border-radius: 5px;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #333333;
        color: #FFFFFF;
    }
    
    /* Tabelas Brancas com bordas pretas */
    .stTable { 
        background-color: #FFFFFF !important; 
        color: #000000 !important; 
        border: 1px solid #000000; 
    }
    </style>
    """, unsafe_allow_html=True)

# 2. GESTÃO DE DADOS (VERSÃO V14 - RESET TOTAL)
# Usar nomes novos para os arquivos não carregar erros antigos
DB_V = "logistica_aura_v14_viagens.csv"
DB_P = "logistica_aura_v14_passageiros.csv"

def carregar_bancos():
    if not os.path.exists(DB_V):
        pd.DataFrame(columns=["Data", "Motorista", "Passageiro", "CC", "Saida", "Voo", "Trajeto", "Hospedagem", "Observacao", "Hotel_RS", "Aereo_RS", "Combust_RS", "Total_RS"]).to_csv(DB_V, index=False)
    if not os.path.exists(DB_P):
        pd.DataFrame(columns=["Nome", "CC_Padrao"]).to_csv(DB_P, index=False)
    return pd.read_csv(DB_V).fillna(""), pd.read_csv(DB_P).fillna("")

df_v, df_p = carregar_bancos()

# 3. BARRA LATERAL (LOGO E MENU)
with st.sidebar:
    # Usando o link oficial da Aura para garantir que carregue
    st.image("https://auraminerals.com/wp-content/themes/aura-minerals/assets/img/logo-aura.png", width=200)
    st.markdown("---")
    menu = st.radio("NAVEGAÇÃO", ["📋 Agenda Motoristas", "📝 Programar Viagem", "👤 Cadastrar Viajante", "💰 Financeiro"])
    st.markdown("---")
    st.caption("Aura Minerals Apoena | v14.0")

# 4. MÓDULOS DO SISTEMA

if menu == "📋 Agenda Motoristas":
    st.header("Agenda de Logística Operacional")
    if not df_v.empty:
        # Mostra apenas o que o motorista precisa ver
        agenda = df_v[["Data", "Motorista", "Passageiro", "Saida", "Voo", "Trajeto", "Hospedagem", "Observacao"]]
        st.table(agenda)
        st.download_button("📥 Baixar Agenda (CSV)", agenda.to_csv(index=False).encode('utf-8-sig'), "agenda_motoristas.csv", "text/csv")
    else:
        st.info("Nenhuma viagem cadastrada no sistema.")

elif menu == "📝 Programar Viagem":
    st.header("Programar Nova Viagem")
    if df_p.empty:
        st.warning("⚠️ Cadastre um viajante primeiro no menu lateral.")
    else:
        # Busca passageiros cadastrados
        passag_lista = sorted(df_p["Nome"].tolist())
        p_sel = st.selectbox("Selecione o Passageiro", passag_lista)

        with st.form("form_v14"):
            c1, c2 = st.columns(2)
            data_v = c1.date_input("Data da Viagem")
            mot_v = c1.selectbox("Motorista", ["Ilson", "Antonio"])
            saida_v = c1.text_input("Horário Saída")
            voo_v = c2.text_input("Voo / Horário Chegada")
            hosp_v = c2.text_input("Hotel / Destino")
            obs_v = st.text_area("Observações (Aparece na Agenda)")
            
            if st.form_submit_button("✅ SALVAR NA AGENDA"):
                nova_viagem = pd.DataFrame([{
                    "Data": data_v.strftime('%d/%m/%Y'), "Motorista": mot_v, "Passageiro": p_sel, 
                    "CC": "Ver Cadastro", "Saida": saida_v, "Voo": voo_v, "Trajeto": "-", "Hospedagem": hosp_v,
                    "Observacao": obs_v, "Hotel_RS": 0.0, "Aereo_RS": 0.0, "Combust_RS": 0.0, "Total_RS": 0.0
                }])
                pd.concat([df_v, nova_viagem], ignore_index=True).to_csv(DB_V, index=False)
                st.success("Viagem salva com sucesso!")
                st.rerun()

elif menu == "👤 Cadastrar Viajante":
    st.header("Cadastro de Funcionários")
    with st.form("cad_p_v14"):
        nome_n = st.text_input("Nome Completo").upper()
        if st.form_submit_button("CADASTRAR"):
            if nome_n:
                novo_p = pd.DataFrame([{"Nome": nome_n, "CC_Padrao": "Geral"}])
                pd.concat([df_p, novo_p], ignore_index=True).to_csv(DB_P, index=False)
                st.success(f"{nome_n} cadastrado!")
                st.rerun()

elif menu == "💰 Financeiro":
    st.header("Gestão de Custos")
    if not df_v.empty:
        df_ed = st.data_editor(df_v)
        if st.button("Salvar Valores Financeiros"):
            df_ed.to_csv(DB_V, index=False)
            st.success("Dados Financeiros Atualizados!")
    else:
        st.info("Nenhuma viagem para calcular custos.")
