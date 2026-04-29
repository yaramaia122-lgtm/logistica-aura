import streamlit as st
import pandas as pd
from github import Github
import io
from datetime import datetime

# 1. Prevenção contra tradutor e ajuste de idioma
st.markdown('<html lang="pt-br">', unsafe_allow_html=True)

st.set_page_config(page_title="Logística Aura Apoena", layout="wide")

# 2. Identidade Visual Harmônica (Engenharia de UI)
st.markdown("""
    <style>
    /* Fundo Geral */
    .stApp { background-color: #F8F9FA; }
    
    /* Barra Lateral - Azul Marinho Aura */
    [data-testid="stSidebar"] {
        background-color: #002D5E !important;
    }
    
    /* Textos da Barra Lateral */
    [data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] label, [data-testid="stSidebar"] p {
        color: white !important;
    }

    /* Estilização das Caixas de Entrada (Inputs) */
    .stTextInput input, .stSelectbox div[data-baseweb="select"], .stDateInput input {
        background-color: #FFFFFF !important;
        border: 1.5px solid #DCE1E7 !important;
        color: #333333 !important;
        border-radius: 8px !important;
    }
    
    /* Foco no Input (Cor de destaque ao clicar) */
    .stTextInput input:focus {
        border-color: #002D5E !important;
    }

    /* Botões - Harmonia entre Cinza e Azul */
    div.stButton > button {
        background-color: #002D5E;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 0.6rem 1rem;
        font-weight: 600;
        transition: all 0.2s ease-in-out;
    }
    
    div.stButton > button:hover {
        background-color: #E8E8E8 !important;
        color: #002D5E !important;
        border: 1px solid #002D5E !important;
    }

    /* Títulos e Tabelas */
    h1, h2, h3 { color: #002D5E; font-weight: 700; }
    [data-testid="stDataFrame"] { background-color: white; border-radius: 10px; padding: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 3. Conexão com Banco de Dados
def carregar_banco():
    try:
        g = Github(st.secrets["GITHUB_TOKEN"])
        repo = g.get_repo("yaramaia122-lgtm/logistica-aura")
        contents = repo.get_contents("dados_logistica.csv")
        df = pd.read_csv(io.StringIO(contents.decoded_content.decode()))
        return df, contents.sha, repo
    except:
        return pd.DataFrame(columns=["Passageiro", "Motorista", "Data", "Trajeto"]), None, None

df, sha, repo = carregar_banco()

# 4. Barra Lateral (Sidebar)
with st.sidebar:
    # Correção da Logo: Usando st.image com a URL raw correta
    logo_url = "https://raw.githubusercontent.com/yaramaia122-lgtm/logistica-aura/main/Aura%20(Azul%20e%20Ocre)%20(1).png"
    st.image(logo_url, use_container_width=True)
    
    st.markdown("<br>", unsafe_allow_html=True) # Espaçador
    menu = st.radio("Selecione a Opção:", ["📋 Agenda", "📝 Programar Viagem", "💰 Financeiro / Edição"])

# 5. Telas do Aplicativo
if menu == "📝 Programar Viagem":
    st.title("📝 Programar Nova Viagem")
    with st.form("form_viagem"):
        col1, col2 = st.columns(2)
        with col1:
            p = st.text_input("Nome do Passageiro").upper()
            m = st.selectbox("Motorista", ["Ilson", "Antonio", "Outro"])
        with col2:
            d = st.date_input("Data da Viagem", datetime.now())
            t = st.selectbox("Trajeto", ["P. Lacerda x Cuiabá", "Interno", "Outro"])
        
        btn_salvar = st.form_submit_button("Confirmar e Salvar")
        
        if btn_salvar:
            if p and repo:
                novo_dado = pd.DataFrame([[p, m, d.strftime('%d/%m/%Y'), t]], columns=df.columns)
                df_final = pd.concat([df, novo_dado], ignore_index=True)
                csv_data = df_final.to_csv(index=False)
                if sha:
                    repo.update_file("dados_logistica.csv", "Registro de Viagem", csv_data, sha)
                else:
                    repo.create_file("dados_logistica.csv", "Início do Banco", csv_data)
                st.success(f"Viagem para {p} registrada!")
                st.rerun()

elif menu == "📋 Agenda":
    st.title("📋 Agenda de Logística")
    if df.empty:
        st.info("Nenhuma viagem programada no momento.")
    else:
        st.dataframe(df, use_container_width=True)

elif menu == "💰 Financeiro / Edição":
    st.title("💰 Gestão e Edição de Dados")
    st.markdown("Use esta tabela para ajustar valores ou excluir linhas:")
    df_editado = st.data_editor(df, num_rows="dynamic", use_container_width=True)
    
    if st.button("Salvar Todas as Alterações"):
        if repo:
            csv_editado = df_editado.to_csv(index=False)
            repo.update_file("dados_logistica.csv", "Edição Manual", csv_editado, sha)
            st.success("Banco de dados atualizado com sucesso!")
            st.rerun()
