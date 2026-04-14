import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="Logística Aura", layout="wide", page_icon="🚛")

# Nome do arquivo onde os dados serão guardados no servidor
DB_FILE = "dados_logistica.csv"

# Função para carregar os dados
def carregar_dados():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    else:
        # Se não existir, cria a estrutura vazia
        return pd.DataFrame(columns=["Data", "Motorista", "Passageiro", "Area", "Saida", "Voo", "Trajeto"])

# Função para salvar os dados
def salvar_dados(df):
    df.to_csv(DB_FILE, index=False)

st.title("🚛 Sistema de Logística Aura - Lançador")
st.markdown("---")

menu = st.sidebar.radio("Navegação", ["Lançar Viagem", "Agenda e Exportação"])

df = carregar_dados()

if menu == "Lançar Viagem":
    st.header("📝 Nova Programação")
    with st.form("form_viagem", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            data = st.date_input("Data da Viagem", datetime.now())
            motorista = st.selectbox("Motorista", ["Ilson", "Antonio", "Terceirizado"])
            passageiro = st.text_input("Nome do Passageiro")
            area = st.selectbox("Área", ["Moagem", "Laboratório", "Mina", "RH", "Segurança"])
        
        with col2:
            saida = st.text_input("Horário de Saída (ex: 06:00)")
            voo = st.text_input("Voo (ex: Latam 3895)")
            trajeto = st.selectbox("Trajeto", ["P. LACERDA X CUIABÁ", "CUIABÁ X P. LACERDA"])

        if st.form_submit_button("✅ Salvar Viagem"):
            if passageiro:
                nova_linha = pd.DataFrame([{
                    "Data": data.strftime('%d/%m/%Y'),
                    "Motorista": motorista,
                    "Passageiro": passageiro,
                    "Area": area,
                    "Saida": saida,
                    "Voo": voo,
                    "Trajeto": trajeto
                }])
                df = pd.concat([df, nova_linha], ignore_index=True)
                salvar_dados(df)
                st.success(f"Viagem de {passageiro} salva com sucesso!")
            else:
                st.error("Por favor, preencha o nome do passageiro.")

elif menu == "Agenda e Exportação":
    st.header("📊 Dados Registrados")
    if not df.empty:
        st.dataframe(df, use_container_width=True)
        
        # BOTÃO DE EXPORTAÇÃO
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Baixar Planilha para Enviar",
            data=csv,
            file_name=f"logistica_aura_{datetime.now().strftime('%d_%m_%Y')}.csv",
            mime="text/csv",
        )
    else:
        st.info("Ainda não há dados lançados.")
