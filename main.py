import streamlit as st
import pandas as pd
from github import Github
import io
from datetime import datetime

# 1. PREVENÇÃO CONTRA TRADUTOR E IDIOMA
st.markdown('<html lang="pt-br">', unsafe_allow_html=True)

# 2. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Aura Apoena Logistics", layout="wide")

# 3. UI/UX PREMIUM DESIGN
st.markdown("""
    <style>
    /* Fundo Principal - Estilo Soft Enterprise */
    .stApp { background-color: #FFFFFF; }
    
    /* Barra Lateral - Azul Marinho Aura */
    [data-testid="stSidebar"] {
        background-color: #002D5E !important;
        min-width: 280px;
    }
    
    /* Textos da Barra Lateral */
    [data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] p, [data-testid="stSidebar"] label {
        color: #FFFFFF !important;
    }

    /* ESTILIZAÇÃO DAS CAIXAS (Inputs) - Azul Claríssimo Moderno */
    .stTextInput input, .stSelectbox div[data-baseweb="select"], .stDateInput input {
        background-color: #F0F4F8 !important; /* Azul muito claro */
        border: 1px solid #D1D9E6 !important;
        color: #002D5E !important; /* Escrita em Marinho */
        border-radius: 10px !important;
        height: 48px !important;
        font-size: 16px !important;
    }
    
    /* Hover e Foco nos Inputs */
    .stTextInput input:focus {
        border-color: #002D5E !important;
        background-color: #FFFFFF !important;
    }

    /* BOTÕES - Estilo "Pense Grande" (Azul Pastel com Marinho) */
    div.stButton > button {
        background-color: #E1E8F0; /* Azul claro harmônico */
        color: #002D5E !important;
        border: 1px solid #002D5E;
        border-radius: 10px;
        padding: 0.8rem 2rem;
        font-weight: 700;
        width: 100%;
        transition: all 0.3s ease;
    }
    
    div.stButton > button:hover {
        background-color: #002D5E !important;
        color: #FFFFFF !important;
        box-shadow: 0 4px 12px rgba(0,45,94,0.2);
    }

    /* Títulos e Tabelas */
    h1, h2, h3 { 
        color: #002D5E !important; 
        letter-spacing: -0.5px;
    }

    /* Data Editor / Tabelas */
    [data-testid="stDataFrame"] {
        background-color: #F8FAFC;
        border-radius: 12px;
        padding: 5px;
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
        return pd.DataFrame(columns=["Passageiro", "Motorista", "Data", "Trajeto"]), None, None

df, sha, repo = carregar_sistema()

# 5. SIDEBAR / MENU
with st.sidebar:
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Tentativa de carregar logo.png (Renomeie sua imagem no GitHub para logo.png)
    try:
        st.image("logo.png", width=240)
    except:
        # Link de backup se o nome ainda estiver com caracteres especiais
        st.image("https://raw.githubusercontent.com/yaramaia122-lgtm/logistica-aura/main/Aura%20(Azul%20e%20Ocre)%20(1).png", width=240)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    menu = st.radio("MÓDULOS:", ["📋 Agenda Global", "📝 Programar Viagem", "💰 Painel de Controle"])

# 6. TELAS
if menu == "📝 Programar Viagem":
    st.title("📝 Programar Viagem")
    with st.form("form_v", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            nome = st.text_input("Nome do Passageiro").upper()
            motorista = st.selectbox("Motorista Designado", ["Ilson", "Antonio", "Outro"])
        with c2:
            data = st.date_input("Data Programada", datetime.now())
            trajeto = st.selectbox("Itinerário", ["P. Lacerda x Cuiabá", "Interno", "Outro"])
        
        if st.form_submit_button("CONCLUIR AGENDAMENTO"):
            if nome and repo:
                nova_viagem = pd.DataFrame([[nome, motorista, data.strftime('%d/%m/%Y'), trajeto]], columns=df.columns)
                df_f = pd.concat([df, nova_viagem], ignore_index=True)
                csv_data = df_f.to_csv(index=False)
                
                if sha:
                    repo.update_file("dados_logistica.csv", "Registro", csv_data, sha)
                else:
                    repo.create_file("dados_logistica.csv", "Init", csv_data)
                
                st.success(f"Logística para {nome} confirmada!")
                st.rerun()

elif menu == "📋 Agenda Global":
    st.title("📋 Fluxo de Viagens")
    st.dataframe(df, width=1400) # Largura ampliada para visão ERP

elif menu == "💰 Painel de Controle":
    st.title("💰 Gestão de Dados")
    st.info("Interface de edição direta no banco de dados.")
    df_editado = st.data_editor(df, num_rows="dynamic", width=1400)
    
    if st.button("SALVAR TODAS AS ALTERAÇÕES"):
        if repo:
            csv_editado = df_editado.to_csv(index=False)
            repo.update_file("dados_logistica.csv", "Edição", csv_editado, sha)
            st.success("Sincronizado com o repositório!")
            st.rerun()
