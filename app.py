import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Configurações Iniciais
st.set_page_config(page_title="Logística Aura", layout="wide", page_icon="🚛")

# Bancos de Dados Internos
DB_VIAGENS = "db_viagens.csv"
DB_PASSAGEIROS = "db_p.csv"

def carregar(file, cols):
    if os.path.exists(file): return pd.read_csv(file)
    return pd.DataFrame(columns=cols)

def salvar(df, file): df.to_csv(file, index=False)

df_v = carregar(DB_VIAGENS, ["Data", "Motorista", "Passageiro", "CC", "Saida", "Voo", "Trajeto", "Hospedagem", "Hotel_Valor", "Aereo_Valor", "Combustivel", "Total"])
df_p = carregar(DB_PASSAGEIROS, ["Nome", "Centro_Custo_Padrao"])

# LISTA INTEGRAL DE CENTROS DE CUSTO (CONFORME SUAS IMAGENS)
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
    "150101 - Administração de Mina - Nosde", "120101 - Administração de Mina - Ernesto",
    "340101 - Exploração Mineral", "320501 - Comunicação", "310901 - Exploração EP",
    "121104 - Geotecnia - Ernesto", "121105 - Hidrogeologia - Ernesto"
])

st.title("🚛 Gestão de Logística Aura")
menu = st.sidebar.radio("Navegação", ["📋 Agenda Motoristas", "📝 Programar Viagem", "👤 Cadastrar Viajante", "💰 Financeiro"])

# 1. AGENDA DO MOTORISTA
if menu == "📋 Agenda Motoristas":
    st.header("📅 Agenda Operacional")
    if not df_v.empty:
        agenda = df_v[["Data", "Motorista", "Passageiro", "Saida", "Voo", "Trajeto", "Hospedagem"]]
        st.dataframe(agenda, use_container_width=True)
        csv = agenda.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 Baixar Agenda para Motoristas", csv, "agenda_operacional.csv", "text/csv", key='btn_agenda')
    else:
        st.info("Nenhuma viagem programada.")

# 2. PROGRAMAR VIAGEM (CC EDITÁVEL E TRAJETO LIVRE)
elif menu == "📝 Programar Viagem":
    st.header("📝 Nova Programação")
    if df_p.empty:
        st.warning("Cadastre o viajante primeiro no menu lateral.")
    else:
        # Seletor de passageiro fora do form para buscar o CC padrão automaticamente
        nome_sel = st.selectbox("Selecione o Passageiro", sorted(df_p["Nome"].tolist()))
        cc_default = df_p[df_p["Nome"] == nome_sel]["Centro_Custo_Padrao"].values[0]

        with st.form("f_v", clear_on_submit=True):
            col1, col2 = st.columns(2)
            data_v = col1.date_input("Data da Viagem")
            mot_v = col1.selectbox("Motorista", ["Ilson", "Antonio"])
            
            # OPÇÃO DE TROCAR O CC AQUI:
            cc_v = col2.selectbox("Centro de Custo desta Viagem", LISTA_CC, index=LISTA_CC.index(cc_default))
            
            saida_v = col1.text_input("Horário Saída (Ex: 06:00)")
            voo_v = col2.text_input("Voo / Horário (Ex: Latam - 04:35)")
            
            st.write("---")
            # TRAJETO FLEXÍVEL
            traj_opc = ["P. LACERDA X CUIABÁ", "CUIABÁ X P. LACERDA", "INTERNO", "OUTRO"]
            traj_s = st.selectbox("Selecione o Trajeto ou 'OUTRO' para digitar", traj_opc)
            traj_m = st.text_input("Se marcou 'OUTRO', digite o local aqui:")
            
            hosp_v = st.text_input("Informação de Hotel / Destino (Ex: Cerrados, Aeroporto)")
            
            if st.form_submit_button("Confirmar e Salvar"):
                t_final = traj_m if traj_s == "OUTRO" else traj_s
                nova = pd.DataFrame([{
                    "Data": data_v.strftime('%d/%m/%Y'), "Motorista": mot_v, "Passageiro": nome_sel, 
                    "CC": cc_v, "Saida": saida_v, "Voo": voo_v, "Trajeto": t_final, "Hospedagem": hosp_v,
                    "Hotel_Valor": 0.0, "Aereo_Valor": 0.0, "Combustivel": 0.0, "Total": 0.0
                }])
                df_v = pd.concat([df_v, nova], ignore_index=True)
                salvar(df_v, DB_VIAGENS)
                st.success("Viagem salva na agenda!")

# 3. CADASTRAR VIAJANTE
elif menu == "👤 Cadastrar Viajante":
    st.header("👤 Cadastro de Funcionário")
    with st.form("f_p", clear_on_submit=True):
        n = st.text_input("Nome Completo").upper()
        c = st.selectbox("Centro de Custo Padrão", LISTA_CC)
        if st.form_submit_button("Cadastrar"):
            if n:
                nova_p = pd.DataFrame([{"Nome": n, "Centro_Custo_Padrao": c}])
                df_p = pd.concat([df_p, nova_p], ignore_index=True)
                salvar(df_p, DB_PASSAGEIROS)
                st.success(f"{n} cadastrado!")

# 4. FINANCEIRO
elif menu == "💰 Financeiro":
    st.header("💰 Gestão de Custos")
    if not df_v.empty:
        df_ed = st.data_editor(df_v)
        df_ed["Total"] = df_ed["Hotel_Valor"] + df_ed["Aereo_Valor"] + df_ed["Combustivel"]
        if st.button("Salvar Fechamento Financeiro"):
            salvar(df_ed, DB_VIAGENS)
            st.success("Custos atualizados!")
