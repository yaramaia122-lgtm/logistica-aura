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
    if os.path.exists(file): 
        try: return pd.read_csv(file)
        except: return pd.DataFrame(columns=cols)
    return pd.DataFrame(columns=cols)

def salvar(df, file): df.to_csv(file, index=False)

# Carregamento de dados
df_v = carregar(DB_VIAGENS, ["Data", "Motorista", "Passageiro", "CC", "Saida", "Voo", "Trajeto", "Hospedagem", "Hotel_Valor", "Aereo_Valor", "Combustivel", "Total"])
df_p = carregar(DB_PASSAGEIROS, ["Nome", "Centro_Custo_Padrao"])

# LISTA INTEGRAL DE CENTROS DE CUSTO
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

# 1. AGENDA
if menu == "📋 Agenda Motoristas":
    st.header("📅 Agenda Operacional")
    if not df_v.empty:
        agenda = df_v[["Data", "Motorista", "Passageiro", "Saida", "Voo", "Trajeto", "Hospedagem"]]
        st.dataframe(agenda, use_container_width=True)
        csv = agenda.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 Baixar Agenda", csv, "agenda.csv", "text/csv", key='btn_agenda_final')
    else: st.info("Nenhuma viagem cadastrada.")

# 2. PROGRAMAR VIAGEM (LÓGICA BLINDADA)
elif menu == "📝 Programar Viagem":
    st.header("📝 Nova Programação")
    if df_p.empty:
        st.warning("⚠️ Cadastre pelo menos um viajante primeiro no menu 'Cadastrar Viajante'.")
    else:
        # Seletor de passageiro
        lista_nomes = sorted(df_p["Nome"].tolist())
        nome_sel = st.selectbox("1. Selecione o Passageiro", lista_nomes)
        
        # Busca o CC padrão de forma segura
        cc_row = df_p[df_p["Nome"] == nome_sel]["Centro_Custo_Padrao"]
        cc_default = cc_row.values[0] if not cc_row.empty else LISTA_CC[0]

        with st.form("form_v2"):
            col1, col2 = st.columns(2)
            data_v = col1.date_input("Data")
            mot_v = col1.selectbox("Motorista", ["Ilson", "Antonio"])
            
            # Centro de Custo: Se o sugerido não estiver na lista, usa o primeiro da lista
            idx_cc = 0
            if cc_default in LISTA_CC:
                idx_cc = LISTA_CC.index(cc_default)
            
            cc_v = col2.selectbox("2. Centro de Custo (Pode alterar)", LISTA_CC, index=idx_cc)
            
            saida_v = col1.text_input("Horário Saída")
            voo_v = col2.text_input("Voo / Horário")
            
            st.write("---")
            traj_s = st.selectbox("Trajeto", ["P. LACERDA X CUIABÁ", "CUIABÁ X P. LACERDA", "INTERNO", "OUTRO"])
            traj_m = st.text_input("Se selecionou 'OUTRO', digite o local:")
            
            hosp_v = st.text_input("Hotel / Destino Final")
            
            if st.form_submit_button("Salvar Viagem"):
                t_final = traj_m if traj_s == "OUTRO" else traj_s
                nova = pd.DataFrame([{
                    "Data": data_v.strftime('%d/%m/%Y'), "Motorista": mot_v, "Passageiro": nome_sel, 
                    "CC": cc_v, "Saida": saida_v, "Voo": voo_v, "Trajeto": t_final, "Hospedagem": hosp_v,
                    "Hotel_Valor": 0.0, "Aereo_Valor": 0.0, "Combustivel": 0.0, "Total": 0.0
                }])
                df_v = pd.concat([df_v, nova], ignore_index=True)
                salvar(df_v, DB_VIAGENS)
                st.success("✅ Salvo com sucesso!")
                st.rerun()

# 3. CADASTRAR VIAJANTE
elif menu == "👤 Cadastrar Viajante":
    st.header("👤 Cadastro de Funcionário")
    with st.form("f_p_cad_safe"):
        n = st.text_input("Nome Completo").upper()
        c = st.selectbox("Centro de Custo Padrão", LISTA_CC)
        if st.form_submit_button("Cadastrar"):
            if n:
                nova_p = pd.DataFrame([{"Nome": n, "Centro_Custo_Padrao": c}])
                df_p = pd.concat([df_p, nova_p], ignore_index=True)
                salvar(df_p, DB_PASSAGEIROS)
                st.success(f"Funcionário {n} cadastrado!")
            else: st.error("O nome não pode estar vazio.")

# 4. FINANCEIRO
elif menu == "💰 Financeiro":
    st.header("💰 Gestão de Custos")
    if not df_v.empty:
        df_ed = st.data_editor(df_v, key="editor_financeiro")
        df_ed["Total"] = df_ed["Hotel_Valor"] + df_ed["Aereo_Valor"] + df_ed["Combustivel"]
        if st.button("Salvar Fechamento Financeiro"):
            salvar(df_ed, DB_VIAGENS)
            st.success("Dados salvos!")
        csv_f = df_ed.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 Baixar
