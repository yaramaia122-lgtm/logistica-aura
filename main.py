import streamlit as st
import pandas as pd
from github import Github
import io
import os
from datetime import datetime

# ==========================================================
# 1. FORÇAR TEMA CLARO (RESOLVE O PROBLEMA DAS TABELAS ESCURAS)
# ==========================================================
def forcar_tema_claro():
    try:
        os.makedirs(".streamlit", exist_ok=True)
        arquivo = ".streamlit/config.toml"
        conteudo = "[theme]\nbase='light'\nprimaryColor='#002D5E'\n"
        
        precisa_escrever = True
        if os.path.exists(arquivo):
            with open(arquivo, "r") as f:
                if conteudo in f.read():
                    precisa_escrever = False
                    
        if precisa_escrever:
            with open(arquivo, "w") as f:
                f.write(conteudo)
    except:
        pass

forcar_tema_claro()

# ==========================================================
# 2. CONFIGURAÇÃO DA PÁGINA
# ==========================================================
st.set_page_config(page_title="Aura Apoena Logistics", layout="wide")

# ==========================================================
# 3. UI/UX - ESTILO DEFINITIVO COM FOCO NAS DESCRIÇÕES DA TABELA
# ==========================================================
st.markdown("""
<style>
    /* Fundo geral limpo */
    .stApp { background-color: #FFFFFF !important; }
    [data-testid="stSidebar"] { background-color: #002D5E !important; }
    [data-testid="stSidebar"] [data-testid="stImage"] img { filter: drop-shadow(0px 10px 15px rgba(0,0,0,0.6)); }
    
    /* Textos Gerais */
    h1, h2, h3, label, .stMarkdown p { color: #002D5E !important; font-weight: 700 !important; opacity: 1 !important; }
    
    /* Campos de Preenchimento: Azul Claro com letra Preta/Azul Escura */
    .stTextInput input, .stSelectbox div[data-baseweb="select"], .stDateInput input, .stNumberInput input { 
        background-color: #F0F7FF !important; 
        border: 2px solid #002D5E !important; 
        border-radius: 6px !important; 
    }
    input { color: #002D5E !important; -webkit-text-fill-color: #002D5E !important; font-weight: 600 !important; }
    div[data-baseweb="select"] span { color: #002D5E !important; font-weight: 600 !important; }
    
    /* Botões */
    div.stButton > button { 
        background-color: #E1E8F0 !important; 
        color: #002D5E !important; 
        border: 2px solid #002D5E !important; 
        font-weight: 800 !important; 
        width: 100% !important; 
        height: 50px !important; 
    }
    
    /* ==========================================================
       NOVO: ESTILO EXCLUSIVO PARA DEIXAR A TABELA VISÍVEL E LINDA 
       ========================================================== */
    table { width: 100%; border-collapse: collapse; }
    
    /* Cabeçalhos (Descrições) - Azul Marinho Forte e Fundo Claro */
    th { 
        background-color: #E1E8F0 !important; 
        color: #002D5E !important; 
        font-weight: 900 !important; 
        font-size: 16px !important;
        border-bottom: 3px solid #002D5E !important;
        padding: 12px !important;
        text-align: left !important;
    }
    
    /* Células com as informações - Fundo Azul Gelo */
    td { 
        background-color: #F0F7FF !important;
        color: #000000 !important; 
        border-bottom: 1px solid #B0C4DE !important;
        padding: 10px !important;
        font-size: 15px !important;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================================
# 4. BACKEND GITHUB
# ==========================================================
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

# ==========================================================
# 5. SIDEBAR / MENU
# ==========================================================
with st.sidebar:
    st.markdown("<br>", unsafe_allow_html=True)
    st.image("https://raw.githubusercontent.com/yaramaia122-lgtm/logistica-aura/main/logo.png", width=220)
    st.markdown("---")
    menu = st.radio("NAVEGAÇÃO", ["Agenda", "Programar Viagem", "Financeiro"])

# ==========================================================
# 6. TELAS E APLICAÇÃO
# ==========================================================
if menu == "Agenda":
    st.title("📋 Agenda de Viagens")
    
    # Substituí st.dataframe por st.table. Isso força o HTML a desenhar as cores perfeitas do CSS.
    if not df.empty:
        st.table(df[["Passageiro", "Motorista", "Data", "Trajeto", "Obs"]])
    else:
        st.info("Nenhuma viagem agendada.")

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
    
    st.info("💡 Como o Tema Claro foi ativado pelo código, esta tabela de edição também voltará a ficar com leitura fácil.")
    df_ed = st.data_editor(df, num_rows="dynamic", use_container_width=True)
    
    if st.button("SALVAR ALTERAÇÕES FINANCEIRAS"):
        if repo:
            df_ed["Total"] = df_ed["Hotel"] + df_ed["Combustivel"] + df_ed["Aereo"] + df_ed["Outros"]
            repo.update_file("dados_logistica.csv", "Financeiro", df_ed.to_csv(index=False), sha)
            st.success("✅ ALTERAÇÕES REGISTRADAS!")
            st.rerun()
