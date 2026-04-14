import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 1. CONFIGURAÇÃO DA PÁGINA (FORÇANDO O TEMA)
st.set_page_config(page_title="Aura Minerals - Logística", layout="wide")

# CSS para garantir que o fundo fique branco e os títulos em Azul Aura
st.markdown("""
    <style>
    .stApp { background-color: white; }
    h1, h2, h3, p, span { color: #002D5E !important; }
    .stTable { background-color: white; color: #002D5E; }
    </style>
    """, unsafe_allow_html=True)

# 2. BANCO DE DADOS
DB_VIAGENS = "db_viagens.csv"
DB_PASSAGEIROS = "db_p.csv"

def carregar(file, cols):
    if os.path.exists(file): 
        try: return pd.read_csv(file)
        except: return pd.DataFrame(columns=cols)
    return pd.DataFrame(columns=cols)

def salvar(df, file): df.to_csv(file, index=False)

COLS_V = ["Data", "Motorista", "Passageiro", "CC", "Saida", "Voo", "Trajeto", "Hospedagem", "Observacao", "Hotel_Valor", "Aereo_Valor", "Combustivel", "Total"]
df_v = carregar(DB_VIAGENS, COLS_V)
df_p = carregar(DB_PASSAGEIROS, ["Nome", "Centro_Custo_Padrao"])

# LISTA COMPLETA DE CC (Resumo do seu PDF)
LISTA_CC = sorted([
    "210301 - Moagem", "210403 - Detox", "210801 - Laboratório", "211002 - Manut. Mecânica",
    "210101 - Admin. Planta", "320101 - Suprimentos", "320301 - RH", "121101 - Geologia",
    "310501 - Meio Ambiente", "310503 - Segurança Trabalho", "310502 - Saude"
])

# 3. LOGO E MENU
# Usando a logo oficial da Aura via URL estável
st.sidebar.image("https://auraminerals.com/wp-content/themes/aura-minerals/assets/img/logo-aura.png", width=150)
st.sidebar.markdown("---")
menu = st.sidebar.radio("Navegação", ["📅 Agenda Motoristas", "📝 Programar Viagem", "👤 Cadastrar Viajante", "💰 Financeiro"])

# 4. MÓDULOS
if menu == "📅 Agenda Motoristas":
    st.header("Agenda de Logística Operacional")
    if not df_v.empty:
        # Tabela limpa com campo de observação
        agenda = df_v[["Data", "Motorista", "Passageiro", "Saida", "Voo", "Trajeto", "Hospedagem", "Observacao"]]
        st.table(agenda)
        
        csv = agenda.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 Exportar Agenda para Motoristas", csv, "agenda_aura.csv", "text/csv")
    else:
        st.info("Nenhuma viagem programada.")

elif menu == "📝 Programar Viagem":
    st.header("Nova Programação")
    if df_p.empty:
        st.warning("Cadastre o viajante primeiro.")
    else:
        # Proteção para não dar erro se o nome sumir
        lista_nomes = sorted(df_p["Nome"].tolist())
        nome_sel = st.selectbox("Selecione o Passageiro", lista_nomes)
        cc_default = df_p[df_p["Nome"] == nome_sel]["Centro_Custo_Padrao"].iloc[0]

        with st.form("form_viagem_v6"):
            col1, col2 = st.columns(2)
            data_v = col1.date_input("Data da Viagem")
            mot_v = col1.selectbox("Motorista", ["Ilson", "Antonio"])
            
            try: idx_cc = LISTA_CC.index(cc_default)
            except: idx_cc = 0
            cc_v = col2.selectbox("Centro de Custo (Rateio)", LISTA_CC, index=idx_cc)
            
            saida_v = col1.text_input("Horário Saída")
            voo_v = col2.text_input("Voo / Horário")
            
            traj_opc = ["P. LACERDA X CUIABÁ", "CUIABÁ X P. LACERDA", "INTERNO", "OUTRO"]
            traj_s = col1.selectbox("Trajeto", traj_opc)
            traj_m = col1.text_input("Se 'OUTRO', digite aqui")
            
            hosp_v = col2.text_input("Hotel ou Destino Final")
            obs_v = st.text_area("Observação Importante")
            
            if st.form_submit_button("Salvar Programação"):
                t_final = traj_m if traj_s == "OUTRO" else traj_s
                nova = pd.DataFrame([{
                    "Data": data_v.strftime('%d/%m/%Y'), "Motorista": mot_v, "Passageiro": nome_sel, 
                    "CC": cc_v, "Saida": saida_v, "Voo": voo_v, "Trajeto": t_final, "Hospedagem": hosp_v,
                    "Observacao": obs_v, "Hotel_Valor": 0.0, "Aereo_Valor": 0.0, "Combustivel": 0.0, "Total": 0.0
                }])
                df_v = pd.concat([df_v, nova], ignore_index=True)
                salvar(df_v, DB_VIAGENS)
                st.success("✅ Viagem salva na agenda!")
                st.rerun()

elif menu == "👤 Cadastrar Viajante":
    st.header("Cadastro de Viajantes")
    with st.form("form_cad"):
        n = st.text_input("Nome Completo").upper()
        c = st.selectbox("CC Padrão", LISTA_CC)
        if st.form_submit_button("Cadastrar"):
            if n:
                nova_p = pd.DataFrame([{"Nome": n, "Centro_Custo_Padrao": c}])
                df_p = pd.concat([df_p, nova_p], ignore_index=True)
                salvar(df_p, DB_PASSAGEIROS)
                st.success("Funcionário Cadastrado!")
                st.rerun()

elif menu == "💰 Financeiro":
    st.header("Gestão de Custos e Rateio")
    if not df_v.empty:
        # Editor com lista suspensa no CC
        df_ed = st.data_editor(
            df_v,
            column_config={"CC": st.column_config.SelectboxColumn("CC", options=LISTA_CC)},
            key="editor_aura"
        )
        df_ed["Total"] = df_ed["Hotel_Valor"] + df_ed["Aereo_Valor"] + df_ed["Combustivel"]
        if st.button("Salvar Valores"):
            salvar(df_ed, DB_VIAGENS)
            st.success("Dados Financeiros Atualizados!")
        
        csv_f = df_ed.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 Baixar Relatório Completo", csv_f, "financeiro_aura.csv")
