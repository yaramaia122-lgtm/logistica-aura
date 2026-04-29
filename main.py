import streamlit as st
import pandas as pd
from github import Github
import io
from datetime import datetime

# 1. CONFIGURACAO
st.markdown('<html lang="pt-br">', unsafe_allow_html=True)
st.set_page_config(page_title="Aura Apoena Logistics", layout="wide")

# 2. UI/UX - DESIGN CONGELADO (AZUL CLARO E LETRAS PRETAS)
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    [data-testid="stSidebar"] { background-color: #002D5E !important; min-width: 280px; }
    
    /* SOMBRA NA LOGO */
    [data-testid="stSidebar"] [data-testid="stImage"] img {
        filter: drop-shadow(0px 10px 15px rgba(0,0,0,0.7));
    }

    /* CAIXAS DE ENTRADA - AZUL CLARO / LETRAS PRETAS */
    .stTextInput input, .stSelectbox div[data-baseweb="select"], .stDateInput input, .stNumberInput input {
        background-color: #F0F7FF !important; 
        border: 2px solid #002D5E !important;
        color: #000000 !important;
        border-radius: 8px !important;
        height: 45px !important;
    }
    
    input, div[data-baseweb="select"] span { color: #000000 !important; }

    /* LABELS EM MARINHO */
    label, .stMarkdown p { color: #002D5E !important; font-weight: bold !important; }

    /* BOTOES - AZUL CLARO / TEXTO MARINHO */
    div.stButton > button {
        background-color: #E1E8F0 !important;
        color: #002D5E !important;
        border: 2px solid #002D5E !important;
        font-weight: 700 !important;
        width: 100% !important;
        height: 50px !important;
    }
    
    [data-testid="stSidebar"] .stMarkdown p, [data-testid="stSidebar"] label { color: #FFFFFF !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. BACKEND - CONEXAO GITHUB
def carregar_sistema():
    colunas = ["Passageiro", "Motorista", "Data", "Trajeto", "Obs Itinerario", "Hotel", "Combustivel", "Aereo", "Outros", "Total"]
    try:
        g = Github(st.secrets["GITHUB_TOKEN"])
        repo = g.get_repo("yaramaia122-lgtm/logistica-aura")
        contents = repo.get_contents("dados_logistica.csv")
        df = pd.read_csv(io.StringIO(contents.decoded_content.decode()))
        for col in colunas:
            if col not in df.columns:
                df[col] = 0.0 if col in ["Hotel", "Combustivel", "Aereo", "Outros", "Total"] else ""
        return df, contents.sha, repo
    except:
        return pd.DataFrame(columns=colunas), None, None

df, sha, repo = carregar_sistema()

# 4. SIDEBAR
with st.sidebar:
    st.markdown("<br>", unsafe_allow_html=True)
    # Link da logo - Nomeado como logo.png no seu GitHub
    logo_url = "https://raw.githubusercontent.com/yaramaia122-lgtm/logistica-aura/main/logo.png"
    st.image(logo_url, width=220)
    st.markdown("<br>", unsafe_allow_html=True)
    menu = st.radio("NAVEGACAO:", ["Agenda", "Programar Viagem", "Financeiro"])

# 5. TELAS

if menu == "Agenda":
    st.title("📋 Agenda de Viagens")
    if not df.empty:
        st.dataframe(df[["Passageiro", "Motorista", "Data", "Trajeto", "Obs Itinerario"]], use_container_width=True)
    else:
        st.info("Nenhum registro.")

elif menu == "Programar Viagem":
    st.title("📝 Programar Viagem")
    with st.form("form_v", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            nome = st.text_input("Nome do Passageiro").upper()
            motorista = st.selectbox("Motorista", ["Ilson", "Antonio", "Outro"])
            v_hotel = st.number_input("Valor Hotel (R$)", min_value=0.0)
            v_aereo = st.number_input("Valor Aéreo (R$)", min_value=0.0)
        with c2:
            data = st.date_input("Data da Viagem", datetime.now())
            trajeto = st.selectbox("Itinerario", ["P. Lacerda x Cuiabá", "Interno", "Outro"])
            v_comb = st.number_input("Valor Combustivel (R$)", min_value=0.0)
            v_outros = st.number_input("Outros Custos (R$)", min_value=0.0)
        
        obs = st.text_input("Descricao de Outros / Observacoes")

        if st.form_submit_button("GRAVAR REGISTRO"):
            if nome and repo:
                total = v_hotel + v_comb + v_aereo + v_outros
                nova_linha = pd.DataFrame([[nome, motorista, data.strftime('%d/%m/%Y'), trajeto, obs, v_hotel, v_comb, v_aereo, v_outros, total]], columns=df.columns)
                df_final = pd.concat([df, nova_linha], ignore_index=True)
                csv_data = df_final.to_csv(index=False)
                
                # Feedback e Salvamento
                repo.update_file("dados_logistica.csv", "Update", csv_data, sha)
                st.success("✅ VIAGEM PROGRAMADA")
                st.rerun()

elif menu == "Financeiro":
    st.title("💰 Financeiro")
    df_edit = st.data_editor(df, num_rows="dynamic", use_container_width=True)
    
    if st.button("CONFIRMAR ALTERACOES"):
        if repo:
            df_edit["Total"] = df_edit["Hotel"] + df_edit["Combustivel"] + df_edit["Aereo"] + df_edit["Outros"]
            csv_edit = df_edit.to_csv(index=False)
            repo.update_file("dados_logistica.csv", "Edit", csv_edit, sha)
            st.success("✅ ALTERACOES REGISTRADAS")
            st.rerun()
