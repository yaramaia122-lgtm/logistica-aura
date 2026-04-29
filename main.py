import streamlit as st
import pandas as pd
from github import Github
import io
from datetime import datetime

# 1. PREVENÇÃO CONTRA TRADUTOR E IDIOMA
st.markdown('<html lang="pt-br">', unsafe_allow_html=True)

# 2. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Logística Aura Apoena", layout="wide")

# 3. UI/UX DESIGNER (ESTILIZAÇÃO DAS CORES)
st.markdown("""
    <style>
    /* Fundo Principal */
    .stApp { background-color: #FDFDFD; }
    
    /* Barra Lateral - Azul Marinho Aura */
    [data-testid="stSidebar"] {
        background-color: #002D5E !important;
        min-width: 300px;
    }
    
    /* Ajuste de cor dos textos na Barra Lateral */
    [data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] p, [data-testid="stSidebar"] label {
        color: #FFFFFF !important;
        font-weight: 500;
    }

    /* Estilização das Caixas de Texto (Fundo Branco e Escrita Preta) */
    .stTextInput input, .stSelectbox div[data-baseweb="select"], .stDateInput input {
        background-color: #FFFFFF !important;
        border: 2px solid #002D5E !important;
        color: #000000 !important; /* TEXTO EM PRETO PARA LEITURA */
        border-radius: 6px !important;
        height: 45px !important;
    }
    
    /* Garante que o texto dentro do menu de seleção também fique preto */
    div[data-baseweb="select"] > div {
        color: #000000 !important;
    }

    /* Títulos e Cabeçalhos */
    h1, h2, h3 { 
        color: #002D5E !important; 
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    /* Botão Salvar - Estilo Profissional */
    div.stButton > button {
        background-color: #002D5E;
        color: #FFFFFF;
        border: none;
        border-radius: 6px;
        padding: 0.7rem 1.5rem;
        font-size: 16px;
        font-weight: bold;
        width: 100%;
    }
    
    div.stButton > button:hover {
        background-color: #E8E8E8 !important;
        color: #002D5E !important;
        border: 1px solid #002D5E !important;
    }

    /* Tabela de Dados */
    [data-testid="stDataFrame"] {
        border: 1px solid #E0E0E0;
        border-radius: 8px;
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
    
    # ESTRATÉGIA DE LOGO: Tenta carregar o arquivo local logo.png
    try:
        st.image("logo.png", width=250)
    except:
        # Se não achar o arquivo local, tenta o link direto (RAW)
        # Note que se o nome no GitHub tiver espaços/parênteses, esse link falha.
        st.image("https://raw.githubusercontent.com/yaramaia122-lgtm/logistica-aura/main/logo.png", width=250)
    
    st.markdown("---")
    menu = st.radio("Navegação", ["📋 Agenda de Viagens", "📝 Programar Nova Viagem", "💰 Financeiro e Edição"])

# 6. TELAS
if menu == "📝 Programar Nova Viagem":
    st.title("📝 Programar Nova Viagem")
    with st.form("form_logistica"):
        c1, c2 = st.columns(2)
        with c1:
            nome = st.text_input("Passageiro (Nome Completo)").upper()
            motorista = st.selectbox("Motorista", ["Ilson", "Antonio", "Outro"])
        with c2:
            data = st.date_input("Data da Viagem", datetime.now())
            trajeto = st.selectbox("Trajeto", ["P. Lacerda x Cuiabá", "Interno", "Outro"])
        
        if st.form_submit_button("Confirmar Agendamento"):
            if nome and repo:
                nova_viagem = pd.DataFrame([[nome, motorista, data.strftime('%d/%m/%Y'), trajeto]], columns=df.columns)
                df_atualizado = pd.concat([df, nova_viagem], ignore_index=True)
                csv_txt = df_atualizado.to_csv(index=False)
                
                if sha:
                    repo.update_file("dados_logistica.csv", "Registro de Viagem", csv_txt, sha)
                else:
                    repo.create_file("dados_logistica.csv", "Início do Banco", csv_txt)
                
                st.success(f"Viagem para {nome} salva com sucesso!")
                st.rerun()
            else:
                st.error("Preencha o nome do passageiro antes de salvar.")

elif menu == "📋 Agenda de Viagens":
    st.title("📋 Agenda de Logística")
    if df.empty:
        st.info("Não há viagens registradas no momento.")
    else:
        st.dataframe(df, width=1200)

elif menu == "💰 Financeiro e Edição":
    st.title("💰 Gestão de Registros")
    st.markdown("Edite os dados diretamente na tabela abaixo e clique em salvar:")
    
    df_editado = st.data_editor(df, num_rows="dynamic", width=1200)
    
    if st.button("Salvar Todas as Alterações"):
        if repo:
            csv_editado = df_editado.to_csv(index=False)
            repo.update_file("dados_logistica.csv", "Edição Manual", csv_editado, sha)
            st.success("Dados atualizados no GitHub!")
            st.rerun()
