import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Conexão com a planilha Google
conn = st.connection("gsheets", type=GSheetsConnection)

# Tabela de Centros de Custo extraída do seu PDF [cite: 1, 2]
MAPA_CC = {
    "Moagem": "210301", "Detox": "210403", "Laboratório": "210801",
    "Manutenção Mecânica Planta": "211002", "Administração Planta": "210101",
    "Segurança do Trabalho": "310503", "Saude": "310502", "Meio Ambiente": "310501"
}

st.title("🚛 Logística Aura - Pontes e Lacerda x Cuiabá")

# Menu de navegação baseado no seu controle atual
menu = st.sidebar.selectbox("Navegação", ["Painel do Motorista", "Programar Viagem", "Lançar Custos"])

if menu == "Painel do Motorista":
    st.header("📋 Agenda do Dia")
    # Mostra os horários de saída e voo conforme sua tabela atual
    df = conn.read(worksheet="Viagens")
    if not df.empty:
        st.dataframe(df[['Saída Individual', 'Passageiro', 'Voo', 'Trajeto', 'Motorista']])
