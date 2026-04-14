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

# LISTA COMPLETA DE CENTROS DE CUSTO
LISTA_CC = [
    "210301 - Moagem", "210403 - Detox", "210801 - Laboratório", "211002 - Manut. Mecânica Planta",
    "210405 - Lixiviação/Cianetação", "210101 - Administração Planta", "211001 - Manut. Elétrica Planta",
    "211003 - Oficina Manut. Planta", "210201 - Britagem Primária", "210604 - Fundição",
    "310101 - Almoxarifado", "320401 - Controladoria/Contabilidade", "310701 - Serviços Gerais",
    "320601 - Célula Gestão Contratos", "320101 - Suprimentos", "320502 - TI",
    "311202 - Care and Maintenance SF", "330102 - Apoena Corporativo", "311203 - Care and Maintenance PPQ",
    "340101 - Exploração Mineral", "311201 - Care and Maintenance EP", "320301 - RH",
    "310801 - Portaria e Vigilância", "320501 - Comunicação", "320201 - Jurídico",
    "121101 - Geologia Operacional", "121001 - Planejamento de Mina", "110101 - Adm. de Mina",
    "310501 - Meio Ambiente", "310503 - Segurança do Trabalho", "310502 - Saúde"
]

st.title("🚛 Gestão de Logística Aura - Pontes e Lacerda")
menu = st.sidebar.radio("Navegação", ["📋 Agenda Motoristas", "📝 Programar Viagem", "👤 Cadastrar Viajante", "💰 Financeiro"])

# 1. AGENDA DO MOTORISTA (COM INFORMAÇÃO DE HOTEL/DESTINO)
if menu == "📋 Agenda Motoristas":
    st.header("📅 Programação Operacional para Motoristas")
    if not df_v.empty:
        # Mostra o destino/hotel para o motorista saber para onde levar
        agenda = df_v[["Data", "Motorista", "Passageiro", "Saida", "Voo", "Trajeto", "Hospedagem"]]
        st.dataframe(agenda, use_container_width=True)
        
        csv = agenda.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 Baixar Agenda (Enviar para Ilson/Antonio)", csv, "agenda_logistica.csv", "text/csv")
    else:
        st.info("Nenhuma viagem programada.")

# 2. PROGRAMAR VIAGEM (CC FLEXÍVEL E DESTINO/HOTEL)
elif menu == "📝 Programar Viagem":
    st.header("📝 Nova Programação")
    if df_p.empty:
        st.warning("Cadastre o viajante primeiro no menu lateral.")
    else:
        with st.form("f_v", clear_on_submit=True):
            col1, col2 = st.columns(2)
            data = col1.date_input("Data")
            mot = col1.selectbox("Motorista", ["Ilson", "Antonio"])
            
            # Seleção de Passageiro
            passag_nome = col2.selectbox("Passageiro", sorted(df_p["Nome"].tolist()))
            cc_sugerido = df_p[df_p["Nome"] == passag_nome]["Centro_Custo_Padrao"].values[0]
            
            # Centro de Custo Flexível (Pode mudar na hora da viagem)
            cc_viagem = col2.selectbox("Centro de Custo desta Viagem", LISTA_CC, index=LISTA_CC.index(cc_sugerido))
            
            saida = col1.text_input("Horário Saída (Ex: 06:00)")
            voo = col2.text_input("Voo/Horário (Ex: Latam 3895 - 04:35)")
            
            traj = col1.selectbox("Trajeto", ["P. LACERDA X CUIABÁ", "CUIABÁ X P. LACERDA", "INTERNO"])
            hosp = col2.text_input("Destino/Hotel (Ex: Hotel Cerrados, Plaza ou Direto Aeroporto)")
            
            if st.form_submit_button("Salvar Programação"):
                nova = pd.DataFrame([{
                    "Data": data.strftime('%d/%m/%Y'), "Motorista": mot, "Passageiro": passag_nome, 
                    "CC": cc_viagem, "Saida": saida, "Voo": voo, "Trajeto": traj, "Hospedagem": hosp,
                    "Hotel_Valor": 0, "Aereo_Valor": 0, "Combustivel": 0, "Total": 0
                }])
                df_v = pd.concat([df_v, nova], ignore_index=True)
                salvar(df_v, DB_VIAGENS)
                st.success("Viagem salva na agenda operacional!")

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
        st.write("Insira os valores das notas fiscais:")
        df_editado = st.data_editor(df_v)
        df_editado["Total"] = df_editado["Hotel_Valor"] + df_editado["Aereo_Valor"] + df_editado["Combustivel"]
        
        if st.button("Salvar Fechamento"):
            salvar(df_editado, DB_VIAGENS)
            st.success("Custos atualizados!")
        
        csv_fin = df_editado.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 Baixar Relatório Financeiro", csv_fin, "financeiro_aura.csv")
