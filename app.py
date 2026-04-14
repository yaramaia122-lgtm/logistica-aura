import streamlit as st
import pandas as pd
import os
from datetime import datetime

# CONFIGURAÇÃO DE PÁGINA COM CORES AURA
st.set_page_config(page_title="Aura Minerals - Logística", layout="wide", page_icon="🚛")

# Estilização CSS para seguir o Styleguide (Azul e Amarelo Aura)
st.markdown("""
    <style>
    .main { background-color: #f5f5f5; }
    .stButton>button { background-color: #002d5e; color: white; border-radius: 5px; }
    .stDownloadButton>button { background-color: #ffc20e; color: #002d5e; border-radius: 5px; font-weight: bold; }
    h1, h2, h3 { color: #002d5e; font-family: 'Benton Sans', sans-serif; }
    </style>
    """, unsafe_allow_html=True)

# Bancos de Dados Internos
DB_VIAGENS = "db_viagens.csv"
DB_PASSAGEIROS = "db_p.csv"

def carregar(file, cols):
    if os.path.exists(file): 
        try: return pd.read_csv(file)
        except: return pd.DataFrame(columns=cols)
    return pd.DataFrame(columns=cols)

def salvar(df, file): df.to_csv(file, index=False)

# Colunas oficiais incluindo Observação
COLS_V = ["Data", "Motorista", "Passageiro", "CC", "Saida", "Voo", "Trajeto", "Hospedagem", "Observacao", "Hotel_Valor", "Aereo_Valor", "Combustivel", "Total"]
df_v = carregar(DB_VIAGENS, COLS_V)
df_p = carregar(DB_PASSAGEIROS, ["Nome", "Centro_Custo_Padrao"])

# LISTA INTEGRAL DE CENTROS DE CUSTO (STYLEGUIDE AURA)
LISTA_CC = sorted([
    "210301 - Moagem", "210403 - Detox", "210801 - Laboratório", "211002 - Manutenção Mecânica Planta",
    "210405 - Lixiviação / Cianetação", "210101 - Administração Planta", "211001 - Manutencao Eletrica Planta",
    "211003 - Oficina Manutenção Planta", "210201 - Britagem Primária", "210604 - Fundição",
    "310101 - Almoxarifado", "320401 - Controladoria e Contabilidade", "310701 - Serviços Gerais",
    "320601 - Celula de Gestao de Contratos", "320101 - Suprimentos", "320502 - Tecnologia da Informação",
    "311202 - Care and Maintenance SF", "330102 - Apoena Corporativo", "311203 - Care and Maintenance PPQ",
    "340103 - Jurídico", "310801 - Seguranca Patrimonial", "310301 - PCP", "320201 - Gerência Geral",
    "310508 - Comunidades", "320303 - Trainee", "320301 - Recursos Humanos", "310902 - Campo",
    "310904 - Exploração EPP", "121101 - Geologia Operacional - Mina Ernesto", 
    "121102 - Planejamento e Topografia Operacional", "151101 - Geologia Operacional - Mina Nosde",
    "151103 - Geotecnia - Nosde", "210502 - Barragem", "151102 - Planejamento e Topografia - Nosde",
    "310501 - Meio Ambiente", "310503 - Segurança do Trabalho", "310502 - Saude",
    "150101 - Administração de Mina - Nosde", "120101 - Administração de Mina - Ernesto"
])

# SIDEBAR CORPORATIVA
st.sidebar.image("https://auraminerals.com/wp-content/themes/aura-minerals/assets/img/logo-aura.png", width=150)
menu = st.sidebar.radio("SISTEMA DE LOGÍSTICA", ["Agenda Motoristas", "Programar Viagem", "Cadastrar Viajante", "Financeiro"])

# 1. AGENDA MOTORISTAS (LAYOUT CLEAN)
if menu == "Agenda Motoristas":
    st.header("Agenda Operacional de Viagens")
    if not df_v.empty:
        # Colunas operacionais para os motoristas
        agenda = df_v[["Data", "Motorista", "Passageiro", "Saida", "Voo", "Trajeto", "Hospedagem", "Observacao"]]
        st.dataframe(agenda, use_container_width=True)
        
        # EXPORTAÇÃO FORMATO EXCEL/CSV
        csv = agenda.to_csv(index=False).encode('utf-8-sig')
        st.download_button("Download Agenda Operacional (.csv)", csv, f"agenda_aura_{datetime.now().strftime('%d_%m')}.csv", "text/csv", key='btn_agenda_aura')
    else: st.info("Não há viagens programadas para o período.")

# 2. PROGRAMAR VIAGEM
elif menu == "Programar Viagem":
    st.header("Nova Programação de Viagem")
    if df_p.empty:
        st.warning("Cadastre o viajante antes de programar.")
    else:
        nome_sel = st.selectbox("Selecione o Passageiro", sorted(df_p["Nome"].tolist()))
        cc_default = df_p[df_p["Nome"] == nome_sel]["Centro_Custo_Padrao"].iloc[0]

        with st.form("form_viagem_aura", clear_on_submit=True):
            col1, col2 = st.columns(2)
            data_v = col1.date_input("Data")
            mot_v = col1.selectbox("Motorista", ["Ilson", "Antonio"])
            
            try: idx_cc = LISTA_CC.index(cc_default)
            except: idx_cc = 0
            cc_v = col2.selectbox("Centro de Custo", LISTA_CC, index=idx_cc)
            
            saida_v = col1.text_input("Horário de Saída")
            voo_v = col2.text_input("Voo / Horário")
            
            traj_opc = ["P. LACERDA X CUIABÁ", "CUIABÁ X P. LACERDA", "INTERNO", "OUTRO"]
            traj_s = col1.selectbox("Trajeto", traj_opc)
            traj_m = col1.text_input("Se 'OUTRO', especifique:")
            
            hosp_v = col2.text_input("Destino / Hotel")
            obs_v = st.text_area("Observações (Informações adicionais para o motorista)")
            
            if st.form_submit_button("Salvar Programação"):
                t_final = traj_m if traj_s == "OUTRO" else traj_s
                nova = pd.DataFrame([{
                    "Data": data_v.strftime('%d/%m/%Y'), "Motorista": mot_v, "Passageiro": nome_sel, 
                    "CC": cc_v, "Saida": saida_v, "Voo": voo_v, "Trajeto": t_final, "Hospedagem": hosp_v,
                    "Observacao": obs_v, "Hotel_Valor": 0.0, "Aereo_Valor": 0.0, "Combustivel": 0.0, "Total": 0.0
                }])
                df_v = pd.concat([df_v, nova], ignore_index=True)
                salvar(df_v, DB_VIAGENS)
                st.success("Viagem registrada com sucesso.")
                st.rerun()

# 3. CADASTRAR VIAJANTE
elif menu == "Cadastrar Viajante":
    st.header("Cadastro de Funcionário / Viajante")
    with st.form("form_p_aura"):
        n = st.text_input("Nome Completo (Sem abreviações)").upper()
        c = st.selectbox("Centro de Custo Padrão", LISTA_CC)
        if st.form_submit_button("Cadastrar Viajante"):
            if n:
                nova_p = pd.DataFrame([{"Nome": n, "Centro_Custo_Padrao": c}])
                df_p = pd.concat([df_p, nova_p], ignore_index=True)
                salvar(df_p, DB_PASSAGEIROS)
                st.success(f"Funcionário {n} cadastrado.")
                st.rerun()

# 4. FINANCEIRO
elif menu == "Financeiro":
    st.header("Relatório de Custos e Rateio")
    if not df_v.empty:
        # Configuração da tabela financeira com CC em lista suspensa
        df_ed = st.data_editor(
            df_v,
            column_config={
                "CC": st.column_config.SelectboxColumn("Centro de Custo", options=LISTA_CC, required=True),
                "Observacao": st.column_config.TextColumn("Observação", width="large")
            },
            key="ed_aura_fin"
        )
        df_ed["Total"] = df_ed["Hotel_Valor"] + df_ed["Aereo_Valor"] + df_ed["Combustivel"]
        
        if st.button("Salvar Alterações Financeiras"):
            salvar(df_ed, DB_VIAGENS)
            st.success("Dados financeiros atualizados.")
        
        csv_fin = df_ed.to_csv(index=False).encode('utf-8-sig')
        st.download_button("Exportar Relatório Financeiro Completo", csv_fin, "relatorio_logistica_aura.csv", key='btn_fin_aura')
