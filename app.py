import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="Logística Aura", layout="wide")
st.title("🚛 Sistema de Logística Aura")

try:
    # Tenta conectar no Google Sheets
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(worksheet="Viagens")
    
    st.success("✅ Conectado à sua planilha oficial!")
    
    menu = st.sidebar.radio("Navegação", ["Agenda Atual", "Programar Viagem", "Lançar Custos"])

    if menu == "Agenda Atual":
        st.subheader("📋 Viagens Programadas")
        st.dataframe(df, use_container_width=True)
        # Botão de exportar para você mandar por e-mail
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Baixar Planilha", data=csv, file_name="logistica_aura.csv")

    elif menu == "Programar Viagem":
        st.header("📝 Novo Lançamento")
        with st.form("v_form"):
            p = st.text_input("Passageiro")
            m = st.selectbox("Motorista", ["Ilson", "Antonio"])
            s = st.text_input("Saída")
            v = st.text_input("Voo")
            if st.form_submit_button("Salvar"):
                nova_l = pd.DataFrame([{"Passageiro": p, "Motorista": m, "Saida": s, "Voo": v}])
                atual = pd.concat([df, nova_l], ignore_index=True)
                conn.update(worksheet="Viagens", data=atual)
                st.success("Salvo na Planilha Google!")

except Exception as e:
    st.error("Erro de conexão. O sistema não achou sua planilha antiga.")
    st.info("Se quiser usar o sistema 'em branco' sem erros, me avise!")
