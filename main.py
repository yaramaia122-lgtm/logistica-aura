import streamlit as st
import pandas as pd
from github import Github
import io
from datetime import datetime

# 1. CONFIGURAÇÃO
st.set_page_config(page_title="Aura Apoena Logistics", layout="wide")

# 2. UI/UX - ESTILO ATUALIZADO (FOCO NA VISIBILIDADE DA TABELA)
st.markdown("""
<style>
    .stApp { background-color: #FFFFFF !important; }
    [data-testid="stSidebar"] { background-color: #002D5E !important; }
    [data-testid="stSidebar"] [data-testid="stImage"] img { filter: drop-shadow(0px 10px 15px rgba(0,0,0,0.6)); }
    
    /* Títulos e Labels */
    h1, h2, h3, label, .stMarkdown p { color: #002D5E !important; font-weight: 700 !important; opacity: 1 !important; }
    
    /* Campos de Preenchimento */
    .stTextInput input, .stSelectbox div[data-baseweb="select"], .stDateInput input, .stNumberInput input { 
        background-color: #F0F7FF !important; 
        border: 2px solid #002D5E !important; 
        color: #002D5E !important; 
        border-radius: 8px !important; 
    }
    
    /* Forçar letra Azul Escuro */
    input { color: #002D5E !important; -webkit-text-fill-color: #002D5E !important; font-weight: 600 !important; }
    div[data-baseweb="select"] span { color: #002D5E !important; font-weight: 600 !important; }
    
    /* Botões */
    div.stButton > button { background-color: #E1E8F0 !important; color: #002D5E !important; border: 2px solid #002D5E !important; font-weight: 800 !important; width: 100% !important; height: 55px !important; }
    
    /* === TABELAS: Forçando Cores no Streamlit === */
    /* Fundo Azul Claro */
    [data-testid="stDataFrame"], [data-testid="stDataEditor"] {
        background-color: #F0F7FF !important;
    }
    
    /* Letras Azul Escuro nos cabeçalhos e células */
    [data-testid="stDataFrame"] th, 
    [data-testid="stDataFrame"] td,
    [data-testid="stDataEditor"] th,
    [data-testid="stDataEditor"] td,
    .stDataFrame th, 
    .stDataFrame td,
    table th, 
    table td {
        color: #002D5E !important;
    }
    
    /* Negrito apenas nos cabeçalhos */
    [data-testid="stDataFrame"] th,
    [data-testid="stDataEditor"] th,
    .stDataFrame th,
    table th {
        font-weight: 800 !important;
    }
</style>
""", unsafe_allow_html=True)

# 3. BACKEND GITHUB
def carregar_dados():
    cols = ["Passageiro", "Motorista", "Data", "Trajeto", "Obs", "Hotel", "Combustivel", "Aereo", "Outros", "Total"]
    try:
        g = Github(st.secrets["GITHUB_TOKEN"])
        repo = g.get_repo("yaramaia122-lgtm/logistica-aura")
        contents = repo.get_contents("dados_logistica.csv")
        df = pd.read_csv(io.StringIO(contents.decoded_content.decode()))
        for c in cols:
            if c not in df.columns: df[c] = 0.0 if c in ["Hotel", "Combustivel", "Aereo", "Outros", "Total"] else ""
        return df, contents.sha, repo
    except:
        return pd.DataFrame(columns=cols), None, None

df, sha, repo = carregar_dados()

# 4. SIDEBAR
with st.sidebar:
    st.markdown("<br>", unsafe_allow_html=True)
    st.image("https://raw.githubusercontent.com/yaramaia122-lgtm/logistica-aura/main/logo.png", width=220)
    st.markdown("---")
    menu = st.radio("NAVEGAÇÃO", ["Agenda", "Programar Viagem", "Financeiro"])

# 5. TELAS
if menu == "Agenda":
    st.title("📋 Agenda de Viagens")
    st.dataframe(df[["Passageiro", "Motorista", "Data", "Trajeto", "Obs"]], use_container_width=True)

elif menu == "Programar Viagem":
    st.title("📝 Programar Viagem")
    
    form = st.form("meu_form", clear_on_submit=True)
    
    col1, col2 = form.columns(2)
    
    nome = col1.text_input("Nome do Passageiro").upper()
    moto = col1.selectbox("Motorista Designado", ["Ilson", "Antonio", "Outro"])
    v_h = col1.number_input("Custo Hotel (R$)", min_value=0.0)
    v_a = col1.number_input("Custo Aéreo (R$)", min_value=0.0)
    
    data = col2.date_input("Data da Viagem", datetime.now())
    traj = col2.selectbox("Itinerário Principal", ["P. Lacerda x Cuiabá", "Interno", "Outro"])
    v_c = col2.number_input("Custo Combustível (R$)", min_value=0.0)
    v_o = col2.number_input("Outros Custos (R$)", min_value=0.0)
    
    obs = form.text_input("Observações Adicionais")
    
    gravar = form.form_submit_button("GRAVAR REGISTRO NO SISTEMA")

    if gravar:
        if nome and repo:
            total = v_h + v_c + v_a + v_o
            nova_viagem = pd.DataFrame([[nome, moto, data.strftime('%d/%m/%Y'), traj, obs, v_h, v_c, v_a, v_o, total]], columns=df.columns)
            df_final = pd.concat([df, nova_viagem], ignore_index=True)
            
            repo.update_file("dados_logistica.csv", "Registro", df_final.to_csv(index=False), sha)
            st.success("✅ VIAGEM PROGRAMADA COM SUCESSO!")
            st.rerun()
        else:
            st.error("Preencha o passageiro e verifique a conexão.")

elif menu == "Financeiro":
    st.title("💰 Controle Financeiro")
    df_ed = st.data_editor(df, num_rows="dynamic", use_container_width=True)
    
    if st.button("SALVAR ALTERAÇÕES FINANCEIRAS"):
        if repo:
            df_ed["Total"] = df_ed["Hotel"] + df_ed["Combustivel"] + df_ed["Aereo"] + df_ed["Outros"]
            repo.update_file("dados_logistica.csv", "Financeiro", df_ed.to_csv(index=False), sha)
            st.success("✅ ALTERAÇÕES REGISTRADAS!")
            st.rerun()
