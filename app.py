import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Configurações Iniciais
st.set_page_config(page_title="Logística Aura", layout="wide", page_icon="🚛")

# Bancos de Dados Internos (Arquivos salvos no servidor)
DB_VIAGENS = "db_viagens.csv"
DB_PASSAGEIROS = "db_p.csv"

def carregar(file, cols):
    if os.path.exists(file): return pd.read_csv(file)
    return pd.DataFrame(columns=cols)

def salvar(df, file): df.to_csv(file, index=False)

# Carregamento de dados
df_v = carregar(DB_VIAGENS, ["Data", "Motorista", "Passageiro", "CC", "Saida", "Voo", "Trajeto", "Hotel", "Aereo", "Combustivel", "Total"])
df_p = carregar(DB_PASSAGEIROS, ["Nome", "Centro_Custo"])

# --- LISTA COMPLETA DE CENTROS DE CUSTO (EXTRAÍDO DAS IMAGENS) ---
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

st.title("🚛 Gestão de Logística Aura")
menu = st.sidebar.radio("Menu Principal", ["📋 Agenda Motoristas", "📝 Programar Viagem", "👤 Cadastrar Viajante", "💰 Financeiro e Custos"])

# 1. AGENDA DO MOTORISTA (VISÃO LIMPA)
if menu == "📋 Agenda Motoristas":
    st.header("📅 Programação Operacional (Semana)")
    if not df_v.empty:
        # Filtra apenas o operacional para o Ilson e Antonio
        agenda = df_v[["Data", "Motorista", "Passageiro", "Saida", "Voo", "Trajeto"]]
        st.dataframe(agenda, use_container_width=True)
        
        csv = agenda.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 Baixar Agenda para Motoristas", csv, f"agenda_{datetime.now().strftime('%d_%m')}.csv", "text/csv")
    else:
        st.info("Nenhuma viagem programada.")

# 2. PROGRAMAR VIAGEM
elif menu == "📝 Programar Viagem":
    st.header("Nova Programação")
    with st.form("f_v", clear_on_submit=True):
        col1, col2 = st.columns(2)
        data = col1.date_input("Data da Viagem")
        mot = col1.selectbox("Motorista", ["Ilson", "Antonio"])
        passag = col2.selectbox("Passageiro", sorted(df_p["Nome"].tolist())) if not df_p.empty else col2.text_input("Nome (Cadastre o viajante antes)")
        saida = col1.text_input("Horário Saída (Ex: 06:00)")
        voo = col2.text_input("Voo/Horário (Ex: Latam 3895 - 04:35)")
        traj = st.selectbox("Trajeto", ["P. LACERDA X CUIABÁ", "CUIABÁ X P. LACERDA", "OUTRO"])
        
        if st.form_submit_button("Salvar Viagem"):
            cc_p = df_p[df_p["Nome"] == passag]["Centro_Custo"].values[0]
            nova = pd.DataFrame([{
                "Data": data.strftime('%d/%m/%Y'), "Motorista": mot, "Passageiro": passag, 
                "CC": cc_p, "Saida": saida, "Voo": voo, "Trajeto": traj,
                "Hotel": 0, "Aereo": 0, "Combustivel": 0, "Total": 0
            }])
            df_v = pd.concat([df_v, nova], ignore_index=True)
            salvar(df_v, DB_VIAGENS)
            st.success("Viagem salva com sucesso!")

# 3. CADASTRAR VIAJANTE
elif menu == "👤 Cadastrar Viajante":
    st.header("Cadastro de Colaboradores")
    with st.form("f_p", clear_on_submit=True):
        nome = st.text_input("Nome Completo").upper()
        cc = st.selectbox("Selecione o Centro de Custo", sorted(LISTA_CC))
        if st.form_submit_button("Cadastrar Funcionário"):
            if nome:
                nova_p = pd.DataFrame([{"Nome": nome, "Centro_Custo": cc}])
                df_p = pd.concat([df_p, nova_p], ignore_index=True)
                salvar(df_p, DB_PASSAGEIROS)
                st.success(f"{nome} cadastrado!")
            else: st.warning("Digite o nome.")

# 4. FINANCEIRO (EXCLUSIVO SEU)
elif menu == "💰 Financeiro e Custos":
    st.header("📊 Gestão de Custos e Rateio")
    if not df_v.empty:
        st.write("Edite os valores abaixo (Hotel, Aéreo, Combustível):")
        df_editado = st.data_editor(df_v)
        
        # Calcula o total automático
        df_editado["Total"] = df_editado["Hotel"] + df_editado["Aereo"] + df_editado["Combustivel"]
        
        if st.button("Salvar Fechamento Financeiro"):
            salvar(df_editado, DB_VIAGENS)
            st.success("Dados financeiros atualizados!")
        
        st.markdown("---")
        csv_full = df_editado.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 Baixar Relatório Completo para o Financeiro", csv_full, "relatorio_final_logistica.csv")
    else:
        st.info("Lance as viagens primeiro para habilitar o financeiro.")
