import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Bancos de Dados Internos
DB_VIAGENS = "db_viagens.csv"
DB_PASSAGEIROS = "db_p.csv"

def carregar(file, cols):
    if os.path.exists(file): 
        try: return pd.read_csv(file)
        except: return pd.DataFrame(columns=cols)
    return pd.DataFrame(columns=cols)

def salvar(df, file): df.to_csv(file, index=False)

# Colunas Oficiais (Layout do Excel)
COLS_V = ["Data", "Motorista", "Passageiro", "CC", "Saida", "Voo", "Trajeto", "Hospedagem", "Observacao", "Hotel_Valor", "Aereo_Valor", "Combustivel", "Total"]
df_v = carregar(DB_VIAGENS, COLS_V)
df_p = carregar(DB_PASSAGEIROS, ["Nome", "Centro_Custo_Padrao"])

# LISTA DE CENTROS DE CUSTO (TODOS DO MAPA)
LISTA_CC = sorted([
    "210301 - Moagem", "210403 - Detox", "210801 - Laboratório", "211002 - Manut. Mecânica Planta",
    "210405 - Lixiviação / Cianetação", "210101 - Admin. Planta", "211001 - Manut. Elétrica Planta",
    "320101 - Suprimentos", "320301 - RH", "121101 - Geologia Ernesto", "151101 - Geologia Nosde",
    "310501 - Meio Ambiente", "310503 - Segurança Trabalho", "310502 - Saude"
])

st.title("Aura Minerals - Logística Operacional")

menu = st.sidebar.selectbox("MENU", ["Agenda Motoristas", "Programar Viagem", "Viajantes", "Financeiro"])

# 1. AGENDA PARA OS MOTORISTAS
if menu == "Agenda Motoristas":
    st.subheader("Agenda de Viagens")
    if not df_v.empty:
        # Colunas conforme o Excel solicitado
        agenda = df_v[["Data", "Motorista", "Passageiro", "Saida", "Voo", "Trajeto", "Hospedagem", "Observacao"]]
        st.table(agenda) # st.table fica mais parecido com o padrão impresso
        
        csv = agenda.to_csv(index=False).encode('utf-8-sig')
        st.download_button("Exportar Agenda Operacional (CSV)", csv, "agenda_motoristas.csv", key='btn_op')
    else:
        st.info("Nenhuma programação para exibir.")

# 2. PROGRAMAR VIAGEM
elif menu == "Programar Viagem":
    st.subheader("Nova Programação")
    if df_p.empty:
        st.warning("Cadastre um viajante primeiro.")
    else:
        nome_sel = st.selectbox("Passageiro", sorted(df_p["Nome"].tolist()))
        cc_default = df_p[df_p["Nome"] == nome_sel]["Centro_Custo_Padrao"].iloc[0]

        with st.form("form_viagem_v5"):
            col1, col2 = st.columns(2)
            data_v = col1.date_input("Data")
            mot_v = col1.selectbox("Motorista", ["Ilson", "Antonio"])
            cc_v = col2.selectbox("Centro de Custo", LISTA_CC, index=LISTA_CC.index(cc_default))
            
            saida_v = col1.text_input("Horário Saída")
            voo_v = col2.text_input("Voo / Horário")
            
            traj_opc = ["P. LACERDA X CUIABÁ", "CUIABÁ X P. LACERDA", "INTERNO", "OUTRO"]
            traj_s = st.selectbox("Trajeto", traj_opc)
            traj_m = st.text_input("Se 'OUTRO', especifique")
            
            hosp_v = st.text_input("Destino / Hotel")
            obs_v = st.text_area("Observações para o Motorista")
            
            if st.form_submit_button("Confirmar Programação"):
                t_final = traj_m if traj_s == "OUTRO" else traj_s
                nova = pd.DataFrame([{
                    "Data": data_v.strftime('%d/%m/%Y'), "Motorista": mot_v, "Passageiro": nome_sel, 
                    "CC": cc_v, "Saida": saida_v, "Voo": voo_v, "Trajeto": t_final, "Hospedagem": hosp_v,
                    "Observacao": obs_v, "Hotel_Valor": 0.0, "Aereo_Valor": 0.0, "Combustivel": 0.0, "Total": 0.0
                }])
                df_v = pd.concat([df_v, nova], ignore_index=True)
                salvar(df_v, DB_VIAGENS)
                st.success("Salvo com sucesso!")
                st.rerun()

# 4. FINANCEIRO (RATEIO)
elif menu == "Financeiro":
    st.subheader("Gestão de Custos")
    if not df_v.empty:
        # Edição direta com lista suspensa no CC
        df_ed = st.data_editor(
            df_v,
            column_config={"CC": st.column_config.SelectboxColumn("Centro de Custo", options=LISTA_CC)},
            key="fin_editor"
        )
        df_ed["Total"] = df_ed["Hotel_Valor"] + df_ed["Aereo_Valor"] + df_ed["Combustivel"]
        
        if st.button("Salvar Financeiro"):
            salvar(df_ed, DB_VIAGENS)
            st.success("Custos atualizados!")
        
        csv_fin = df_ed.to_csv(index=False).encode('utf-8-sig')
        st.download_button("Exportar Relatório Financeiro", csv_fin, "financeiro_aura.csv")
    else:
        st.info("Aguardando lançamentos.")

# 3. CADASTRO DE VIAJANTE (PARA MANTER A ORDEM)
elif menu == "Viajantes":
    st.subheader("Cadastro de Funcionários")
    with st.form("form_viajantes"):
        n = st.text_input("Nome Completo").upper()
        c = st.selectbox("Centro de Custo Padrão", LISTA_CC)
        if st.form_submit_button("Cadastrar"):
            nova_p = pd.DataFrame([{"Nome": n, "Centro_Custo_Padrao": c}])
            df_p = pd.concat([df_p, nova_p], ignore_index=True)
            salvar(df_p, DB_PASSAGEIROS)
            st.success("Funcionário Cadastrado!")
            st.rerun()
