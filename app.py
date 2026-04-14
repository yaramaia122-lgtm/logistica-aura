import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 1. SETUP DA PÁGINA (ESTILO AURA)
st.set_page_config(page_title="Aura Minerals - Logística", layout="wide")

# Forçando o fundo branco e títulos em azul via CSS injetado
st.markdown("""
    <style>
    .stApp { background-color: white; }
    h1, h2, h3, h4, p, span, label { color: #002D5E !important; font-family: 'Benton Sans', sans-serif; }
    .stTable { background-color: white; }
    div[data-baseweb="select"] > div { background-color: white; color: #002D5E; }
    .stButton>button { background-color: #002D5E; color: white; border: 1px solid #FFC20E; }
    .stDownloadButton>button { background-color: #FFC20E; color: #002D5E; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 2. GESTÃO DE BANCO DE DADOS (PREVENÇÃO DE ERROS)
DB_V = "viagens_v3.csv"
DB_P = "passageiros_v3.csv"
COLS_VIAGEM = ["Data", "Motorista", "Passageiro", "CC", "Saida", "Voo", "Trajeto", "Hospedagem", "Observacao", "Hotel_R$", "Aereo_R$", "Combust_R$", "Total"]

def inicializar_dbs():
    if not os.path.exists(DB_V): pd.DataFrame(columns=COLS_VIAGEM).to_csv(DB_V, index=False)
    if not os.path.exists(DB_P): pd.DataFrame(columns=["Nome", "CC_Padrao"]).to_csv(DB_P, index=False)

inicializar_dbs()

def carregar_v(): 
    df = pd.read_csv(DB_V)
    return df.reindex(columns=COLS_VIAGEM).fillna(0) if not df.empty else pd.DataFrame(columns=COLS_VIAGEM)

def carregar_p(): return pd.read_csv(DB_P)

# 3. LISTA DE CENTROS DE CUSTO (INTEGRAL)
LISTA_CC = sorted([
    "210301 - Moagem", "210403 - Detox", "210801 - Laboratório", "211002 - Manut. Mecânica",
    "210101 - Admin. Planta", "320101 - Suprimentos", "320301 - RH", "121101 - Geologia",
    "310501 - Meio Ambiente", "310503 - Segurança Trabalho", "310502 - Saude",
    "340101 - Exploração Mineral", "320502 - TI", "150101 - Adm. de Mina - Nosde"
])

# 4. BARRA LATERAL (LOGO E MENU)
st.sidebar.image("https://auraminerals.com/wp-content/themes/aura-minerals/assets/img/logo-aura.png", width=180)
st.sidebar.markdown("<h3 style='color: white;'>LOGÍSTICA APOENA</h3>", unsafe_allow_html=True)
menu = st.sidebar.radio("Navegação", ["📅 Agenda Motoristas", "📝 Programar Viagem", "👤 Cadastrar Viajante", "💰 Financeiro"])

# 5. MÓDULOS
if menu == "📅 Agenda Motoristas":
    st.header("Agenda Operacional de Viagens")
    df = carregar_v()
    if not df.empty:
        # Layout igual ao Excel solicitado
        agenda = df[["Data", "Motorista", "Passageiro", "Saida", "Voo", "Trajeto", "Hospedagem", "Observacao"]]
        st.table(agenda)
        
        csv = agenda.to_csv(index=False).encode('utf-8-sig')
        st.download_button("Exportar Agenda para Motoristas (Excel/CSV)", csv, "agenda_motoristas.csv", "text/csv")
    else: st.info("Nenhuma viagem programada.")

elif menu == "📝 Programar Viagem":
    st.header("Nova Programação")
    df_p = carregar_p()
    if df_p.empty:
        st.warning("Cadastre um viajante primeiro.")
    else:
        # Seletor fora do form para carregar CC padrão
        nomes = sorted(df_p["Nome"].tolist())
        p_sel = st.selectbox("Selecione o Passageiro", nomes)
        cc_sug = df_p[df_p["Nome"] == p_sel]["CC_Padrao"].iloc[0]

        with st.form("f_v3"):
            c1, c2 = st.columns(2)
            data = c1.date_input("Data da Viagem")
            mot = c1.selectbox("Motorista", ["Ilson", "Antonio"])
            
            try: idx = LISTA_CC.index(cc_sug)
            except: idx = 0
            cc_v = c2.selectbox("Centro de Custo (Rateio)", LISTA_CC, index=idx)
            
            saida = c1.text_input("Horário Saída")
            voo = c2.text_input("Voo / Horário")
            
            st.write("---")
            t_s = st.selectbox("Trajeto", ["P. LACERDA X CUIABÁ", "CUIABÁ X P. LACERDA", "INTERNO", "OUTRO"])
            t_m = st.text_input("Se 'OUTRO', digite o destino")
            
            hosp = st.text_input("Hotel / Destino Final")
            obs = st.text_area("Observações (Aparece na Agenda do Motorista)")
            
            if st.form_submit_button("Salvar Viagem"):
                t_f = t_m if t_s == "OUTRO" else t_s
                nova = pd.DataFrame([{
                    "Data": data.strftime('%d/%m/%Y'), "Motorista": mot, "Passageiro": p_sel, 
                    "CC": cc_v, "Saida": saida, "Voo": voo, "Trajeto": t_f, "Hospedagem": hosp,
                    "Observacao": obs, "Hotel_R$": 0.0, "Aereo_R$": 0.0, "Combust_R$": 0.0, "Total": 0.0
                }])
                pd.concat([carregar_v(), nova], ignore_index=True).to_csv(DB_V, index=False)
                st.success("✅ Viagem salva!")
                st.rerun()

elif menu == "👤 Cadastrar Viajante":
    st.header("Cadastro de Viajantes")
    with st.form("f_p3"):
        n = st.text_input("Nome Completo").upper()
        c = st.selectbox("CC Padrão", LISTA_CC)
        if st.form_submit_button("Cadastrar"):
            if n:
                pd.concat([carregar_p(), pd.DataFrame([{"Nome": n, "CC_Padrao": c}])], ignore_index=True).to_csv(DB_P, index=False)
                st.success(f"Funcionário {n} cadastrado!")
                st.rerun()

elif menu == "💰 Financeiro":
    st.header("Gestão de Custos")
    df = carregar_v()
    if not df.empty:
        df_ed = st.data_editor(
            df,
            column_config={"CC": st.column_config.SelectboxColumn("CC", options=LISTA_CC)},
            key="edit_fin_v3"
        )
        df_ed["Total"] = df_ed["Hotel_R$"] + df_ed["Aereo_R$"] + df_ed["Combust_R$"]
        if st.button("Salvar Valores"):
            df_ed.to_csv(DB_V, index=False)
            st.success("Financeiro atualizado!")
        
        csv_f = df_ed.to_csv(index=False).encode('utf-8-sig')
        st.download_button("Baixar Relatório Completo", csv_f, "financeiro_aura.csv")
