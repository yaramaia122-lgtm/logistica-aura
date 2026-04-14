import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Logística Aura", layout="wide", page_icon="🚛")

# Título e Estilo
st.title("🚛 Sistema de Logística - Aura")
st.markdown("---")

try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # Menu lateral para facilitar
    menu = st.sidebar.radio("Navegação", ["Lançar Viagem", "Agenda/Exportar", "Mapa de Custos"])

    if menu == "Lançar Viagem":
        st.header("📝 Nova Programação de Viagem")
        with st.form("form_viagem"):
            col1, col2 = st.columns(2)
            with col1:
                data = st.date_input("Data da Viagem", datetime.now())
                motorista = st.selectbox("Motorista", ["Ilson", "Antonio", "Terceirizado"])
                passageiro = st.text_input("Nome do Passageiro")
                area = st.selectbox("Área/Centro de Custo", ["Moagem", "Laboratório", "Mina", "RH", "Segurança"])
            
            with col2:
                saida = st.text_input("Horário de Saída (ex: 06:00)")
                voo = st.text_input("Voo e Horário (ex: Latam 3895 - 04:35)")
                trajeto = st.selectbox("Trajeto", ["P. LACERDA X CUIABÁ", "CUIABÁ X P. LACERDA", "INTERNO"])

            if st.form_submit_button("✅ Salvar na Planilha"):
                # Aqui o sistema monta a linha para você
                nova_v = pd.DataFrame([{"Data": str(data), "Motorista": motorista, "Passageiro": passageiro, "Area": area, "Saida": saida, "Voo": voo, "Trajeto": trajeto}])
                
                # Tenta ler o que já existe e junta com o novo
                existente = conn.read(worksheet="Viagens")
                atualizado = pd.concat([existente, nova_v], ignore_index=True)
                conn.update(worksheet="Viagens", data=atualizado)
                st.success("Salvo com sucesso! A planilha foi atualizada.")

    elif menu == "Agenda/Exportar":
        st.header("📊 Agenda e Exportação")
        df = conn.read(worksheet="Viagens")
        st.dataframe(df, use_container_width=True)
        
        # O BOTÃO DE EXPORTAR QUE VOCÊ QUERIA:
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Baixar Planilha para Excel (CSV)", data=csv, file_name="logistica_aura.csv", mime="text/csv")

except Exception as e:
    st.error("O sistema está aguardando a conexão com o link da planilha nas Secrets.")
    st.info("Certifique-se de que o link nas Secrets é o da planilha Logistica_Aura como 'Editor'.")
