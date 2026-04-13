import streamlit as st
from gspread_pandas import Spread, conf
import pandas as pd
from datetime import datetime

# --- CONFIGURAÇÃO WEB ---
st.set_page_config(page_title="Aura Logística Web", layout="wide")

# Conexão com Google Sheets (Necessita do arquivo de credenciais da Google)
# Para fins de demonstração, o código assume que as credenciais estão configuradas
PLANILHA_NOME = "Logistica_Aura"

def carregar_dados(aba_nome):
    try:
        # Aqui o Python liga-se à tua planilha na nuvem
        s = Spread(PLANILHA_NOME)
        return s.sheet_to_df(sheet=aba_nome, index=0)
    except:
        return pd.DataFrame()

# --- INTERFACE ---
st.title("🚛 Sistema de Logística e Rateio de Viagens")

aba1, aba2, aba3 = st.tabs(["📋 Programação", "💰 Lançar Custos", "📊 Relatórios por Área"])

with aba1:
    st.header("Nova Programação de Viagem")
    with st.form("nova_viagem"):
        col1, col2 = st.columns(2)
        with col1:
            data = st.date_input("Data da Viagem")
            trajeto = st.selectbox("Trajeto", ["PONTES E LACERDA X CUIABÁ", "CUIABÁ X PONTES E LACERDA"])
            motorista = st.selectbox("Motorista", ["Ilson", "Antonio"])
        
        with col2:
            passageiros = st.multiselect("Passageiros", ["Guilherme", "Fabiele", "José Flavio", "Eduardo"]) # Puxar do cadastro depois
        
        # Horários Individuais
        detalhes = []
        if passageiros:
            for p in passageiros:
                c1, c2 = st.columns(2)
                h_s = c1.time_input(f"Saída de {p}", key=f"s_{p}")
                h_v = c2.time_input(f"Voo de {p}", key=f"v_{p}")
                detalhes.append({"p": p, "saida": h_s.strftime("%H:%M"), "voo": h_v.strftime("%H:%M")})
        
        if st.form_submit_button("Salvar Logística"):
            # Lógica para enviar para o Google Sheets
            st.success("Viagem salva na nuvem! O motorista já consegue visualizar.")

with aba2:
    st.header("Inserir Custos (Combustível, Hotel, Aéreo)")
    st.info("Aqui selecionas as viagens já realizadas e inseres os valores que chegaram depois.")
    # Filtro de viagens sem custo
    viagem_id = st.selectbox("Selecione a Viagem Pendente", ["Viagem 10/04 - Ilson", "Viagem 12/04 - Antonio"])
    
    v_carro = st.number_input("Valor Total Combustível/Traslado", min_value=0.0)
    
    # Exemplo de custos individuais
    st.write("Custos de Hotel e Aéreo por Passageiro:")
    # O sistema gera campos automáticos para cada passageiro daquela viagem
    
    if st.button("Finalizar e Ratear"):
        st.success("Custos processados e divididos por Centro de Custo!")

with aba3:
    st.header("Relatório Consolidado por Centro de Custo")
    # Tabela dinâmica que soma tudo por Descrição de Área (Moagem, Geologia, etc.)
    st.markdown("### Total por Área (Descrição)")
    # Simulação de output
    df_exemplo = pd.DataFrame({
        "Área": ["Moagem", "Laboratório", "Geologia"],
        "Custo Total (R$)": [1250.50, 800.00, 2100.20]
    })
    st.table(df_exemplo)
