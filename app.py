import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 1. CONFIGURAÇÃO DA PÁGINA (FORÇAR TEMA CLARO)
st.set_page_config(
    page_title="Logística Aura Minerals", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# 2. CSS CUSTOMIZADO (CORES: AZUL MARINHO E CINZA)
st.markdown("""
    <style>
    /* Fundo Branco e Texto Azul Marinho */
    .stApp { background-color: #FFFFFF !important; }
    
    /* Barra Lateral Azul Marinho */
    [data-testid="stSidebar"] { background-color: #002D5E !important; }
    [data-testid="stSidebar"] * { color: #FFFFFF !important; }
    
    /* Títulos e Textos */
    h1, h2, h3, p, label { color: #002D5E !important; font-family: 'Segoe UI', sans-serif; }

    /* Estilo dos Campos de Entrada (Cinza Aura) */
    div[data-baseweb="input"], div[data-baseweb="select"], .stTextArea textarea {
        background-color: #E8E8E8 !important;
        border: 1px solid #002D5E !important;
        border-radius: 5px !important;
    }
    input { color: #002D5E !important; }

    /* Botões Padrão Aura */
    .stButton>button {
        background-color: #E8E8E8 !important;
        color: #002D5E !important;
        border: 2px solid #002D5E !important;
        border-radius: 8px !important;
        font-weight: bold !important;
        width: 100%;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #002D5E !important;
        color: #FFFFFF !important;
    }

    /* Logo com Sombra e Alinhamento */
    .logo-container { display: flex; justify-content: center; padding: 20px 0; }
    .logo-aura {
        filter: drop-shadow(0px 4px 10px rgba(0, 0, 0, 0.7));
        width: 180px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. CONFIGURAÇÃO DE CAMINHOS (AJUSTE AQUI) ---
# Substitua pelo caminho da sua pasta de teste do OneDrive
PASTA_ONEDRIVE = r"C:\Users\yara.chaves\OneDrive - Aura Minerals\Apoena - Gerência Administrativa e Financeira-Infraestrutura - Teste"

# Se o caminho acima não for encontrado, ele salva na mesma pasta do código por segurança
if not os.path.exists(PASTA_ONEDRIVE):
    PASTA_FINAL = os.getcwd()
else:
    PASTA_FINAL = PASTA_ONEDRIVE

DB_V = os.path.join(PASTA_FINAL, "banco_viagens_oficial.csv")

# 4. FUNÇÃO DE CARREGAMENTO
def carregar_dados():
    if not os.path.exists(DB_V):
        pd.DataFrame(columns=["Data", "Motorista", "Passageiro", "Trajeto", "Status"]).to_csv(DB_V, index=False)
    return pd.read_csv(DB_V).fillna("")

df_v = carregar_dados()

# 5. BARRA LATERAL (LOGO E MENU)
with st.sidebar:
    st.markdown('<div class="logo-container"><img src="https://gist.githubusercontent.com/user-attachments/assets/8e0f5228-40b9-4674-9f0f-6df3d57b280c" class="logo-aura"></div>', unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: white !important;'>Gestão de Logística</h3>", unsafe_allow_html=True)
    st.markdown("---")
    menu = st.radio("NAVEGAÇÃO", ["📋 Agenda", "📝 Programar Viagem", "💰 Financeiro"])

# 6. MÓDULOS DO SISTEMA
if menu == "📝 Programar Viagem":
    st.header("📝 Programar Nova Viagem")
    with st.form("form_viagem"):
        col1, col2 = st.columns(2)
        nome = col1.text_input("Nome do Passageiro").upper()
        motorista = col1.selectbox("Motorista", ["Ilson", "Antonio", "Outro"])
        data = col2.date_input("Data da Viagem", datetime.now())
        trajeto = col2.selectbox("Trajeto", ["P. LACERDA X CUIABÁ", "CUIABÁ X P. LACERDA", "INTERNO", "OUTRO"])
        
        if st.form_submit_button("✅ SALVAR NO SHAREPOINT"):
            nova_linha = pd.DataFrame([{
                "Data": data.strftime('%d/%m/%Y'),
                "Motorista": motorista,
                "Passageiro": nome,
                "Trajeto": trajeto,
                "Status": "Programado"
            }])
            df_final = pd.concat([df_v, nova_linha], ignore_index=True)
            df_final.to_csv(DB_V, index=False)
            st.success(f"Viagem salva com sucesso em: {PASTA_FINAL}")
            st.rerun()

elif menu == "📋 Agenda":
    st.header("📋 Agenda de Viagens")
    if not df_v.empty:
        st.dataframe(df_v, use_container_width=True)
    else:
        st.info("Nenhuma viagem programada ainda.")

elif menu == "💰 Financeiro":
    st.header("💰 Gestão Financeira e Custos")
    st.markdown("Edite os valores diretamente na tabela abaixo:")
    df_editado = st.data_editor(df_v, use_container_width=True, num_rows="dynamic")
    if st.button("💾 ATUALIZAR PLANILHA"):
        df_editado.to_csv(DB_V, index=False)
        st.success("Planilha atualizada no SharePoint!")
