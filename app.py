import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# Configuração da página
st.set_page_config(page_title="Logística Aura", layout="wide", page_icon="🚛")

st.title("🚛 Logística Aura - Sistema de Controle")

# 1. TENTATIVA DE CONEXÃO
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # Tentativa de ler os dados existentes
    df_viagens = conn.read(worksheet="Viagens", ttl=0)
    
    st.sidebar.success("✅ Planilha Conectada!")
    
    menu = st.sidebar.radio("Navegação", ["Agenda do Dia", "Programar Viagem", "Lançar Custos"])

    # --- ABA: AGENDA DO DIA ---
    if menu == "Agenda do Dia":
        st.header("📋 Agenda Operacional")
        if not df_viagens.empty:
            # Filtra apenas o que é importante para o motorista ver
            st.dataframe(df_viagens, use_container_width=True)
        else:
            st.info("Nenhuma viagem programada na aba 'Viagens'.")

    # --- ABA: PROGRAMAR VIAGEM ---
    elif menu == "Programar Viagem":
        st.header("📝 Cadastrar Nova Viagem")
        
        with st.form("novo_registro"):
            col1, col2 = st.columns(2)
            with col1:
                data = st.date_input("Data", datetime.now())
                motorista = st.selectbox("Motorista", ["Ilson", "Antonio"])
                passageiro = st.text_input("Nome do Passageiro")
            with col2:
                saida = st.text_input("Horário Saída (ex: 06:00)")
                voo = st.text_input("Voo/Horário (ex: Latam 3895 - 04:35)")
                trajeto = st.selectbox("Trajeto", ["P. LACERDA X CUIABÁ", "CUIABÁ X P. LACERDA"])
            
            submit = st.form_submit_button("Confirmar e Salvar")

            if submit:
                if passageiro:
                    # Cria a nova linha
                    nova_linha = pd.DataFrame([{
                        "Data": data.strftime('%d/%m/%Y'),
                        "Motorista": motorista,
                        "Passageiro": passageiro,
                        "Saida": saida,
                        "Voo": voo,
                        "Trajeto": trajeto,
                        "Status": "Pendente"
                    }])
                    
                    # Tenta salvar na planilha
                    try:
                        updated_df = pd.concat([df_viagens, nova_linha], ignore_index=True)
                        conn.update(worksheet="Viagens", data=updated_df)
                        st.success(f"✅ Viagem de {passageiro} salva com sucesso!")
                        st.balloons()
                    except Exception as e_save:
                        st.error(f"Erro ao salvar: Verifique se a planilha está como EDITOR. Detalhe: {e_save}")
                else:
                    st.warning("Por favor, preencha o nome do passageiro.")

except Exception as e:
    st.error("❌ Falha crítica de conexão!")
    st.info("Abaixo está o motivo técnico. Se possível, tire um print desta parte:")
    st.code(str(e))
    
    st.markdown("""
    ### 🛠️ Como resolver agora:
    1. **Na Planilha:** Clique em 'Compartilhar' -> Mude para **'Qualquer pessoa com o link'** -> Mude para **'Editor'**.
    2. **No Streamlit (Secrets):** Verifique se o link termina em `/edit#gid=0` e está entre aspas.
    """)
