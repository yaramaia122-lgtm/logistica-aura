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

# LISTA DE CENTROS DE CUSTO
LISTA_CC = [
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
]

st.title("🚛 Gestão de Logística Aura")
menu = st.sidebar.radio("Navegação", ["📋 Agenda Motoristas", "📝 Programar Viagem", "👤 Cadastrar Viajante", "💰 Financeiro"])

# 1. AGENDA DO MOTORISTA
if menu == "📋 Agenda Motoristas":
    st.header("📅 Agenda Operacional")
    if not df_v.empty:
        agenda = df_v[["Data", "Motorista", "Passageiro", "Saida", "Voo", "Trajeto", "Hospedagem"]]
        st.dataframe(agenda, use_container_width=True)
        csv = agenda.to_csv(index=False).encode('utf-8-sig')
        # ADICIONADO KEY ÚNICA AQUI
        st.download_button("📥 Baixar Agenda para Motoristas", csv, "agenda_operacional.csv", "text/csv", key='btn_agenda')
    else:
        st.info("Nenhuma viagem programada.")

# 2. PROGRAMAR VIAGEM
elif menu == "📝 Programar Viagem":
    st.header("📝 Nova Programação")
    if df_p.empty:
        st.warning("Cadastre o viajante primeiro.")
    else:
        with st.form("f_v", clear_on_submit=True):
            col1, col2 = st.columns(2)
            data = col1.date_input("Data")
            mot = col1.selectbox("Motorista", ["Ilson", "Antonio"])
            passag_nome = col2.selectbox("Passageiro", sorted(df_p["Nome"].tolist()))
            cc_sugerido = df_p[df_p["Nome"] == passag_nome]["Centro_Custo_Padrao"].values[0]
            cc_viagem = col2.selectbox("Centro de Custo desta Viagem", sorted(LISTA_CC), index=sorted(LISTA_CC).index(cc_sugerido))
            saida = col1.text_input("Horário Saída (Ex: 06:00)")
            voo = col2.text_input("Voo/Horário (Ex: Latam - 04:35)")
            traj_opcoes = ["P. LACERDA X CUIABÁ", "CUIABÁ X P. LACERDA", "INTERNO", "OUTRO"]
            traj_sel = st.selectbox("Selecione o Trajeto ou 'OUTRO' para digitar", traj_opcoes)
            
            traj_final = ""
            if traj_sel == "OUTRO":
                traj_final = st.text_input("Digite o Trajeto Personalizado")
            else:
                traj_final = traj_sel
                
            hosp = st.text_input("Informação de Hotel/Destino")
            
            if st.form_submit_button("Salvar na Agenda"):
                nova = pd.DataFrame([{
                    "Data": data.strftime('%d/%m/%Y'), "Motorista": mot, "Passageiro": passag_nome, 
                    "CC": cc_viagem, "Saida": saida, "Voo": voo, "Trajeto": traj_final, "Hospedagem": hosp,
                    "Hotel_Valor": 0.0, "Aereo_Valor": 0.0, "Combustivel": 0.0, "Total": 0.0
                }])
                df_v = pd.concat([df_v, nova], ignore_index=True)
                salvar(df_v, DB_VIAGENS)
                st.success("Viagem programada!")

# 3. CADASTRAR VIAJANTE
elif menu == "👤 Cadastrar Viajante":
    st.header("👤 Cadastro de Funcionário")
    with st.form("f_p", clear_on_submit=True):
        nome = st.text_input("Nome Completo").upper()
        cc_fixo = st.selectbox("Centro de Custo Padrão", sorted(LISTA_CC))
        if st.form_submit_button("Cadastrar"):
            if nome:
                nova_p = pd.DataFrame([{"Nome": nome, "Centro_Custo_Padrao": cc_fixo}])
                df_p = pd.concat([df_p, nova_p], ignore_index=True)
                salvar(df_p, DB_PASSAGEIROS)
                st.success(f"{nome} cadastrado com sucesso!")

# 4. FINANCEIRO
elif menu == "💰 Financeiro":
    st.header("💰 Lançamento de Custos (Rateio)")
    if not df_v.empty:
        df_editado = st.data_editor(df_v)
        df_editado["Total"] = df_editado["Hotel_Valor"] + df_editado["Aereo_Valor"] + df_editado["Combustivel"]
        if st.button("Salvar Fechamento"):
            salvar(df_editado, DB_VIAGENS)
            st.success("Custos salvos!")
        
        csv_fin = df_editado.to_csv(index=False).encode('utf-8-sig')
        # ADICIONADO KEY ÚNICA AQUI TAMBÉM
        st.download_button("📥 Baixar Relatório Financeiro", csv_fin, "financeiro_aura.csv", key='btn_financeiro')
