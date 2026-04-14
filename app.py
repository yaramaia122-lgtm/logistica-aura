import streamlit as st
import pandas as pd
import os
from datetime import datetime
import base64

# 1. IDENTIDADE VISUAL (STYLEGUIDE AURA - DOURADO, BRANCO E PRETO)
st.set_page_config(page_title="Aura Minerals - Logística", layout="wide")

# CSS para forçar o fundo branco e as cores institucionais
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF !important; }
    [data-testid="stSidebar"] { background-color: #FFC20E !important; border-right: 3px solid #000000; }
    [data-testid="stSidebar"] * { color: #000000 !important; font-weight: bold; }
    h1, h2, h3, h4, label, p, span { color: #000000 !important; font-family: 'Benton Sans', sans-serif !important; }
    .stButton>button { background-color: #000000; color: #FFFFFF; border: 2px solid #000000; font-weight: bold; }
    .stButton>button:hover { background-color: #FFC20E; color: #000000; }
    .stDownloadButton>button { background-color: #000000 !important; color: #FFC20E !important; font-weight: bold; border: 2px solid #000000; }
    .stTable { background-color: #FFFFFF !important; color: #000000 !important; border: 1px solid #000000; }
    </style>
    """, unsafe_allow_html=True)

# 2. GESTÃO DE DADOS (VERSÃO V13 - LIMPA)
DB_V = "logistica_v13_viagens.csv"
DB_P = "logistica_v13_passageiros.csv"

def iniciar_bancos():
    if not os.path.exists(DB_V):
        pd.DataFrame(columns=["Data", "Motorista", "Passageiro", "CC", "Saida", "Voo", "Trajeto", "Hospedagem", "Observacao", "Hotel_RS", "Aereo_RS", "Combust_RS", "Total_RS"]).to_csv(DB_V, index=False)
    if not os.path.exists(DB_P):
        pd.DataFrame(columns=["Nome", "CC_Padrao"]).to_csv(DB_P, index=False)
    return pd.read_csv(DB_V).fillna(""), pd.read_csv(DB_P).fillna("")

df_v, df_p = iniciar_bancos()
LISTA_CC = sorted(["210301 - Moagem", "210403 - Detox", "210801 - Laboratório", "211002 - Manut. Mecânica", "320101 - Suprimentos", "310501 - Meio Ambiente"])

# 3. SIDEBAR COM LOGO (MÉTODO INFALÍVEL)
with st.sidebar:
    # Link direto da logo que você enviou (Aura Ocre e Azul)
    st.image("https://auraminerals.com/wp-content/themes/aura-minerals/assets/img/logo-aura.png", width=200)
    st.markdown("---")
    menu = st.radio("NAVEGAÇÃO", ["📋 Agenda Motoristas", "📝 Programar Viagem", "👤 Cadastrar Viajante", "💰 Financeiro"])

# 4. MÓDULOS
if menu == "📋 Agenda Motoristas":
    st.header("Agenda Operacional de Viagens")
    if not df_v.empty:
        # Tabela limpa com fundo branco e bordas pretas
        agenda = df_v[["Data", "Motorista", "Passageiro", "Saida", "Voo", "Trajeto", "Hospedagem", "Observacao"]]
        st.table(agenda)
        st.download_button("📥 Exportar Agenda (CSV)", agenda.to_csv(index=False).encode('utf-8-sig'), "agenda_aura.csv", "text/csv")
    else: st.info("Nenhuma programação encontrada.")

elif menu == "📝 Programar Viagem":
    st.header("Nova Programação")
    if df_p.empty:
        st.warning("Cadastre o viajante primeiro.")
    else:
        lista_nomes = sorted(df_p["Nome"].tolist())
        nome_sel = st.selectbox("Selecione o Passageiro", lista_nomes)
        
        with st.form("f_v13"):
            c1, c2 = st.columns(2)
            data = c1.date_input("Data da Viagem")
            mot = c1.selectbox("Motorista", ["Ilson", "Antonio"])
            saida = c1.text_input("Horário Saída")
            voo = c2.text_input("Voo / Horário")
            hosp = c2.text_input("Hotel / Destino")
            obs = st.text_area("Observações (Aparece na Agenda)")
            
            if st.form_submit_button("Confirmar Viagem"):
                nova = pd.DataFrame([{
                    "Data": data.strftime('%d/%m/%Y'), "Motorista": mot, "Passageiro": nome_sel, 
                    "CC": "A definir", "Saida": saida, "Voo": voo, "Trajeto": "-", "Hospedagem": hosp,
                    "Observacao": obs, "Hotel_RS": 0.0, "Aereo_RS": 0.0, "Combust_RS": 0.0, "Total_RS": 0.0
                }])
                pd.concat([df_v, nova], ignore_index=True).to_csv(DB_V, index=False)
                st.success("✅ Salvo com sucesso!")
                st.rerun()

elif menu == "👤 Cadastrar Viajante":
    st.header("Cadastro de Funcionário")
    with st.form("f_p13"):
        n = st.text_input("Nome Completo").upper()
        if st.form_submit_button("Cadastrar"):
            if n:
                pd.concat([df_p, pd.DataFrame([{"Nome": n, "CC_Padrao": "Geral"}])], ignore_index=True).to_csv(DB_P, index=False)
                st.success(f"{n} cadastrado!")
                st.rerun()

elif menu == "💰 Financeiro":
    st.header("Gestão Financeira")
    if not df_v.empty:
        df_ed = st.data_editor(df_v)
        if st.button("Salvar Valores"):
            df_ed.to_csv(DB_V, index=False)
            st.success("Financeiro atualizado!")
