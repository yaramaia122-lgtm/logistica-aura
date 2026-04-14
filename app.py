import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta

# Configurações iniciais
st.set_page_config(page_title="Logística Aura", layout="wide", page_icon="🚛")

# Arquivos de banco de dados internos
DB_VIAGENS = "db_viagens.csv"
DB_PASSAGEIROS = "db_passageiros.csv"

# Funções de Banco de Dados
def carregar_dados(file, colunas):
    if os.path.exists(file):
        return pd.read_csv(file)
    return pd.DataFrame(columns=colunas)

def salvar_dados(df, file):
    df.to_csv(file, index=False)

# Inicialização
df_v = carregar_dados(DB_VIAGENS, ["Data", "Motorista", "Passageiro", "CC", "Saida", "Voo", "Trajeto", "Custo_Hotel", "Custo_Aereo", "Custo_Carro"])
df_p = carregar_dados(DB_PASSAGEIROS, ["Nome", "Centro_Custo"])

# --- INTERFACE ---
st.title("🚛 Gestão de Logística Independente - Aura")
menu = st.sidebar.radio("Módulos", ["Painel Geral", "Cadastrar Passageiro", "Programar Viagem", "Lançar Custos", "Exportar Relatórios"])

# 1. CADASTRO DE PASSAGEIRO (E CENTRO DE CUSTO)
if menu == "Cadastrar Passageiro":
    st.header("👤 Cadastro de Viajantes")
    with st.form("form_p", clear_on_submit=True):
        nome = st.text_input("Nome Completo")
        cc = st.selectbox("Centro de Custo", ["210301 - Moagem", "210801 - Laboratório", "121101 - Geologia", "320101 - Suprimentos", "Outro"])
        if st.form_submit_button("Salvar Passageiro"):
            if nome:
                nova_p = pd.DataFrame([{"Nome": nome.upper(), "Centro_Custo": cc}])
                df_p = pd.concat([df_p, nova_p], ignore_index=True)
                salvar_dados(df_p, DB_PASSAGEIROS)
                st.success("Passageiro cadastrado!")
            else: st.error("Preencha o nome.")

# 2. PROGRAMAR VIAGEM
elif menu == "Programar Viagem":
    st.header("📝 Programação de Logística")
    if df_p.empty:
        st.warning("Cadastre passageiros primeiro!")
    else:
        with st.form("form_v", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                data = st.date_input("Data da Viagem")
                motorista = st.selectbox("Motorista", ["Ilson", "Antonio", "Terceirizado"])
                passageiro = st.selectbox("Passageiro", df_p["Nome"].tolist())
            with col2:
                saida = st.text_input("Horário de Saída (ex: 06:00)")
                voo = st.text_input("Voo/Horário (ex: Latam 3895 - 04:35)")
                trajeto = st.selectbox("Trajeto", ["P. LACERDA X CUIABÁ", "CUIABÁ X P. LACERDA"])
            
            if st.form_submit_button("Confirmar Programação"):
                # Busca o CC do passageiro automaticamente
                centro_c = df_p[df_p["Nome"] == passageiro]["Centro_Custo"].values[0]
                nova_v = pd.DataFrame([{
                    "Data": data.strftime('%d/%m/%Y'), "Motorista": motorista, 
                    "Passageiro": passageiro, "CC": centro_c, "Saida": saida, 
                    "Voo": voo, "Trajeto": trajeto, "Custo_Hotel": 0, "Custo_Aereo": 0, "Custo_Carro": 0
                }])
                df_v = pd.concat([df_v, nova_v], ignore_index=True)
                salvar_dados(df_v, DB_VIAGENS)
                st.success("Viagem programada!")

# 3. LANÇAR CUSTOS
elif menu == "Lançar Custos":
    st.header("💰 Fechamento Financeiro")
    if df_v.empty: st.info("Nenhuma viagem para lançar custos.")
    else:
        viagem_ref = st.selectbox("Selecione a Viagem", df_v["Passageiro"] + " - " + df_v["Data"])
        idx = df_v[df_v["Passageiro"] + " - " + df_v["Data"] == viagem_ref].index[0]
        
        col1, col2, col3 = st.columns(3)
        h = col1.number_input("Custo Hotel (R$)", min_value=0.0)
        a = col2.number_input("Custo Aéreo (R$)", min_value=0.0)
        c = col3.number_input("Custo Carro/Combustível (R$)", min_value=0.0)
        
        if st.button("Atualizar Custos"):
            df_v.at[idx, "Custo_Hotel"] = h
            df_v.at[idx, "Custo_Aereo"] = a
            df_v.at[idx, "Custo_Carro"] = c
            salvar_dados(df_v, DB_VIAGENS)
            st.success("Valores atualizados!")

# 4. PAINEL E EXPORTAÇÃO
elif menu == "Painel Geral" or menu == "Exportar Relatórios":
    st.header("📊 Relatório de Logística e Custos")
    if not df_v.empty:
        st.dataframe(df_v, use_container_width=True)
        
        # Filtro semanal simples
        csv = df_v.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Baixar Planilha Semanal (Excel/CSV)", data=csv, file_name=f"logistica_semanal_{datetime.now().strftime('%d_%m')}.csv")
    else:
        st.info("Aguardando lançamentos...")
