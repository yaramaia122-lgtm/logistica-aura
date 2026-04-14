import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Configuração da página
st.set_page_config(page_title="Logística Aura", layout="wide")

st.title("🚛 Logística Aura - Controle de Viagens")

# Tentar conectar com a planilha
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # Tentar ler a aba de Viagens
    df = conn.read(worksheet="Viagens")
    
    st.success("✅ Conectado com sucesso à planilha!")
    
    # Menu Lateral
    menu = st.sidebar.selectbox("O que deseja fazer?", ["Ver Agenda", "Programar Viagem", "Lançar Custos"])

    if menu == "Ver Agenda":
        st.header("📋 Agenda do Dia (Motoristas)")
        if not df.empty:
            st.dataframe(df)
        else:
            st.info("A aba 'Viagens' está vazia. Comece a programar!")

    elif menu == "Programar Viagem":
        st.header("📝 Nova Programação")
        with st.form("form_viagem"):
            data = st.date_input("Data da Viagem")
            motorista = st.selectbox("Motorista", ["Ilson", "Antonio"])
            passageiro = st.text_input("Nome do Passageiro")
            saida = st.text_input("Horário de Saída (ex: 06:00)")
            voo = st.text_input("Voo (ex: Latam 3895)")
            
            botao = st.form_submit_button("Salvar Viagem")
            
            if botao:
                st.warning("Função de salvar sendo ativada... Verifique se a planilha está como EDITOR.")

except Exception as e:
    st.error("❌ Erro de Conexão!")
    st.write("Verifique se:")
    st.write("1. O link na Secrets está correto e entre aspas.")
    st.write("2. A planilha está compartilhada como 'Qualquer pessoa com o link' pode EDITAR.")
    st.write("3. O nome da aba na planilha é exatamente 'Viagens'.")
    # Mostra o erro real para o suporte se precisar
    if "401" in str(e) or "403" in str(e):
        st.info("Dica: O Google está bloqueando o acesso. Mude a planilha para 'Qualquer pessoa com o link' -> 'Editor'.")
