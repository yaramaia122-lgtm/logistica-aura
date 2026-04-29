import streamlit as st
import pandas as pd
from github import Github
import io
from datetime import datetime

# 1. PREVENÇÃO CONTRA TRADUTOR E IDIOMA
st.markdown('<html lang="pt-br">', unsafe_allow_html=True)

# 2. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Aura Apoena Logistics", layout="wide")

# 3. UI/UX DESIGNER (SOMENTE ALTERAÇÕES SOLICITADAS)
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    
    /* Barra Lateral */
    [data-testid="stSidebar"] {
        background-color: #002D5E !important;
        min-width: 280px;
    }
    
    /* DESTAQUE DA LOGO COM SOMBRA */
    .logo-shadow {
        filter: drop-shadow(0px 4px 8px rgba(0,0,0,0.5));
        transition: all 0.3s ease;
    }

    /* CAIXAS DE PREENCHIMENTO - Fundo Azul Claro e Letras Pretas */
    .stTextInput input, .stSelectbox div[data-baseweb="select"], .stDateInput input, .stNumberInput input {
        background-color: #F0F7FF !important; 
        border: 1px solid #D1D9E6 !important;
        color: #000000 !important; /* Letras Pretas conforme solicitado */
        border-radius: 8px !important;
        height: 45px !important;
    }
    
    /* Garante que o texto dentro do seletor também seja preto */
    div[data-baseweb="select"] > div {
        color: #000000 !important;
    }

    /* BOTÕES - Azul Claro e Azul Marinho */
    div.stButton > button {
        background-color: #E1E8F0 !important; /* Azul Claro solicitado */
        color: #002D5E !important; /* Azul Marinho solicitado */
        border: 1px solid #002D5E;
        border-radius: 8px;
        font-weight: 700;
        width: 100%;
        height: 50px;
        transition: all 0.3s;
    }
    
    div.stButton > button:hover {
        background-color: #002D5E !important; /* Azul Marinho no hover */
        color: #E1E8F0 !important; /* Azul Claro no hover */
    }

    /* Tabelas e Planilhas */
    [data-testid="stDataFrame"], [data-testid="stTable"], .stDataEditor {
        background-color: #FFFFFF !important;
        border-radius: 10px !important;
    }
    
    h1, h2, h3 { color: #002D5E !important; font-weight: 700; }
    [data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] p, [data-testid="stSidebar"] label {
        color: #FFFFFF !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 4. BACKEND (CONEXÃO GITHUB)
def carregar_sistema():
    try:
        g = Github(st.secrets["GITHUB_TOKEN"])
        repo = g.get_repo("yaramaia122-lgtm/logistica-aura")
        contents = repo.get_contents("dados_logistica.csv")
        df = pd.read_csv(io.StringIO(contents.decoded_content.decode()))
        return df, contents.sha, repo
    except:
        return pd.DataFrame(columns=["Passageiro", "Motorista", "Data", "Trajeto", "Valor (R$)"]), None, None

df, sha, repo = carregar_sistema()
if "Valor (R$)" not in df.columns:
    df["Valor (R$)"] = 0.0

# 5. SIDEBAR / MENU
with st.sidebar:
    st.markdown("<br>", unsafe_allow_html=True)
    
    # URL da logo com aplicação de classe CSS para sombra
    logo_path = "https://raw.githubusercontent.com/yaramaia122-lgtm/logistica-aura/main/Aura%20(Azul%20e%20Ocre)%20(1).png"
    
    # Renderizando a logo com HTML para permitir a sombra (drop-shadow)
    st.markdown(f'<div class="logo-shadow"><img src="{logo_path}" width="240"></div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    menu = st.radio("NAVEGAÇÃO:", ["📋 Agenda de Viagens", "📝 Programar Viagem", "💰 Financeiro"])

# 6. TELAS

if menu == "📋 Agenda de Viagens":
    st.title("📋 Agenda de Viagens")
    st.dataframe(df, use_container_width=True)

elif menu == "📝 Programar Viagem":
    st.title("📝 Programar Viagem")
    with st.form("form_v", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            nome = st.text_input("Nome do Passageiro").upper()
            motorista = st.selectbox("Motorista", ["Ilson", "Antonio", "Outro"])
        with c2:
            data = st.date_input("Data", datetime.now())
            trajeto = st.selectbox("Trajeto", ["P. Lacerda x Cuiabá", "Interno", "Outro"])
        
        valor = st.number_input("Valor da Viagem (R$)", min_value=0.0, step=1.0)
        
        if st.form_submit_button("SALVAR REGISTRO"):
            if nome and repo:
                nova_viagem = pd.DataFrame([[nome, motorista, data.strftime('%d/%m/%Y'), trajeto, valor]], columns=df.columns)
                df_f = pd.concat([df, nova_viagem], ignore_index=True)
                csv_data = df_f.to_csv(index=False)
                if sha:
                    repo.update_file("dados_logistica.csv", "Reg", csv_data, sha)
                else:
                    repo.create_file("dados_logistica.csv", "Init", csv_data)
                st.success(f"Viagem para {nome} salva!")
                st.rerun()

elif menu == "💰 Financeiro":
    st.title("💰 Financeiro")
    df_editado = st.data_editor(df, num_rows="dynamic", use_container_width=True)
    
    if st.button("CONFIRMAR ALTERAÇÕES FINANCEIRAS"):
        if repo:
            csv_editado = df_editado.to_csv(index=False)
            repo.update_file("dados_logistica.csv", "Edit Financeiro", csv_editado, sha)
            st.success("Financeiro atualizado!")
            st.rerun()
