import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 1. CONFIGURAÇÃO VISUAL (STYLEGUIDE AURA)
st.set_page_config(page_title="Logística Aura Apoena", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    [data-testid="stSidebar"] { background-color: #002D5E !important; }
    [data-testid="stSidebar"] * { color: #FFFFFF !important; }
    h1, h2, h3, label, p { color: #002D5E !important; font-family: 'Benton Sans', sans-serif !important; }
    .stButton>button { background-color: #002D5E; color: white; border: 2px solid #FFC20E; }
    .stDownloadButton>button { background-color: #FFC20E !important; color: #002D5E !important; font-weight: bold; }
    .stTable { background-color: #FFFFFF; border: 1px solid #002D5E; }
    </style>
    """, unsafe_allow_html=True)

# 2. BANCO DE DADOS (VERSÃO V4 - LIMPA)
DB_V = "logistica_viagens_v4.csv"
DB_P = "cadastro_passageiros_v4.csv"

def carregar(file, cols):
    if os.path.exists(file):
        try:
            df = pd.read_csv(file)
            return df if not df.empty else pd.DataFrame(columns=cols)
        except: return pd.DataFrame(columns=cols)
    return pd.DataFrame(columns=cols)

def salvar(df, file): df.to_csv(file, index=False)

# Colunas estruturadas conforme seu Excel
COLS_V = ["Data", "Motorista", "Passageiro", "CC", "Saida", "Voo", "Trajeto", "Hospedagem", "Observacao", "Hotel_RS", "Aereo_RS", "Combustivel_RS", "Total_RS"]
df_v = carregar(DB_V, COLS_V)
df_p = carregar(DB_P, ["Nome", "CC_Padrao"])

# LISTA COMPLETA DE CENTROS DE CUSTO (MAPA AURA)
LISTA_CC = sorted([
    "210301 - Moagem", "210403 - Detox", "210801 - Laboratório", "211002 - Manut. Mecânica",
    "210405 - Lixiviação Planta", "210101 - Admin. Planta", "211001 - Manut. Elétrica",
    "320101 - Suprimentos", "320301 - RH", "121101 - Geologia Ernesto", "151101 - Geologia Nosde",
    "310501 - Meio Ambiente", "310503 - Segurança Trabalho", "310502 - Saúde", "310801 - Segurança Patrimonial"
])

# 3. SIDEBAR E LOGO
with st.sidebar:
    # Tenta carregar a logo oficial da Aura
    st.image("https://gist.githubusercontent.com/user-attachments/assets/8e0f5228-40b9-4674-9f0f-6df3d57b280c", width=200)
    st.markdown("---")
    menu = st.radio("NAVEGAÇÃO", ["📋 Agenda Motoristas", "📝 Programar Viagem", "👤 Cadastrar Viajante", "💰 Financeiro"])

# 4. MÓDULOS DO SISTEMA
if menu == "📋 Agenda Motoristas":
    st.header("Agenda de Viagens Operacionais")
    if not df_v.empty:
        # Tabela exibe apenas o necessário para o motorista
        agenda = df_v[["Data", "Motorista", "Passageiro", "Saida", "Voo", "Trajeto", "Hospedagem", "Observacao"]]
        st.table(agenda)
        csv = agenda.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 Baixar Agenda (CSV)", csv, "agenda_aura.csv", "text/csv")
    else: st.info("Nenhuma viagem programada.")

elif menu == "📝 Programar Viagem":
    st.header("Programação de Viagem")
    if df_p.empty:
        st.warning("⚠️ Cadastre um viajante primeiro no menu lateral.")
    else:
        # LÓGICA ANTI-ERRO (ValueError)
        nomes_lista = sorted(df_p["Nome"].tolist())
        passag_sel = st.selectbox("Selecione o Passageiro", nomes_lista)
        
        # Busca CC padrão de forma segura
        cc_row = df_p[df_p["Nome"] == passag_sel]["CC_Padrao"]
        cc_sugerido = cc_row.iloc[0] if not cc_row.empty else LISTA_CC[0]

        with st.form("f_v4_definitivo"):
            col1, col2 = st.columns(2)
            data_v = col1.date_input("Data da Viagem")
            mot_v = col1.selectbox("Motorista", ["Ilson", "Antonio"])
            
            # Garante que o index do CC não quebre
            try: idx_cc = LISTA_CC.index(cc_sugerido)
            except: idx_cc = 0
            
            cc_v = col2.selectbox("Centro de Custo (Pode alterar)", LISTA_CC, index=idx_cc)
            saida_v = col1.text_input("Horário Saída")
            voo_v = col2.text_input("Voo / Horário")
            
            traj_s = st.selectbox("Trajeto", ["P. LACERDA X CUIABÁ", "CUIABÁ X P. LACERDA", "INTERNO", "OUTRO"])
            traj_m = st.text_input("Se 'OUTRO', especifique")
            
            hosp_v = st.text_input("Hotel / Destino Final")
            obs_v = st.text_area("Observações")
            
            if st.form_submit_button("✅ Salvar Programação"):
                t_f = traj_m if traj_s == "OUTRO" else traj_s
                nova_v = pd.DataFrame([{
                    "Data": data_v.strftime('%d/%m/%Y'), "Motorista": mot_v, "Passageiro": passag_sel, 
                    "CC": cc_v, "Saida": saida_v, "Voo": voo_v, "Trajeto": t_f, "Hospedagem": hosp_v,
                    "Observacao": obs_v, "Hotel_RS": 0.0, "Aereo_RS": 0.0, "Combustivel_RS": 0.0, "Total_RS": 0.0
                }])
                salvar(pd.concat([df_v, nova_v], ignore_index=True), DB_V)
                st.success("Viagem salva!")
                st.rerun()

elif menu == "👤 Cadastrar Viajante":
    st.header("Cadastro de Viajantes")
    with st.form("f_p4"):
        nome_n = st.text_input("Nome Completo").upper()
        cc_n = st.selectbox("Centro de Custo Padrão", LISTA_CC)
        if st.form_submit_button("Cadastrar"):
            if nome_n:
                novo_p = pd.DataFrame([{"Nome": nome_n, "CC_Padrao": cc_n}])
                salvar(pd.concat([df_p, novo_p], ignore_index=True), DB_P)
                st.success(f"{nome_n} cadastrado!")
                st.rerun()

elif menu == "💰 Financeiro":
    st.header("Gestão de Custos")
    if not df_v.empty:
        df_ed = st.data_editor(
            df_v,
            column_config={"CC": st.column_config.SelectboxColumn("Setor", options=LISTA_CC)},
            key="ed_v4"
        )
        df_ed["Total_RS"] = df_ed["Hotel_RS"] + df_ed["Aereo_RS"] + df_ed["Combustivel_RS"]
        if st.button("Salvar Financeiro"):
            salvar(df_ed, DB_V)
            st.success("Dados atualizados!")
        csv_f = df_ed.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 Relatório Completo", csv_f, "financeiro.csv")
