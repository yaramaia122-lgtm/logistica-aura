import streamlit as st
import pandas as pd
from github import Github
import io
import base64
import os
from datetime import datetime

# 1. CONFIGURAÇÃO E IDENTIDADE VISUAL (AURA MINERALS)
st.set_page_config(page_title="Logística Aura", layout="wide")

# Função para converter sua logo.png local em código que o navegador entenda
def get_base64_logo(file_path):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    return None

logo_base64 = get_base64_logo("logo.png")
logo_html = f'<img src="data:image/png;base64,{logo_base64}" class="logo-aura" width="180">' if logo_base64 else '<h2 style="color:white;">Aura Logística</h2>'

st.markdown(f"""
    <style>
    .stApp {{ background-color: #FFFFFF !important; }}
    [data-testid="stSidebar"] {{ background-color: #002D5E !important; }}
    [data-testid="stSidebar"] * {{ color: #FFFFFF !important; }}
    h1, h2, h3, label {{ color: #002D5E !important; font-family: 'Segoe UI', sans-serif; }}
    
    /* Inputs e Botões em Cinza Aura e Azul */
    div[data-baseweb="input"], div[data-baseweb="select"] {{
        background-color: #E8E8E8 !important;
        border: 1px solid #002D5E !important;
        border-radius: 4px !important;
    }}
    .stButton>button {{
        background-color: #E8E8E8 !important;
        color: #002D5E !important;
        border: 2px solid #002D5E !important;
        font-weight: bold; width: 100%;
    }}
    .stButton>button:hover {{ background-color: #002D5E !important; color: #FFFFFF !important; }}
    
    /* Sua logo com a sombra personalizada */
    .logo-aura {{ 
        filter: drop-shadow(0px 4px 8px rgba(0,0,0,0.5)); 
        display: block; 
        margin: auto; 
    }}
    </style>
    """, unsafe_allow_html=True)

# 2. CONEXÃO COM O GITHUB (yaramaia122-lgtm/logistica-aura)
def conectar_github():
    try:
        if "GITHUB_TOKEN" not in st.secrets:
            st.error("❌ Erro: 'GITHUB_TOKEN' não configurado nos Secrets.")
            return None
        g = Github(st.secrets["GITHUB_TOKEN"])
        return g.get_repo("yaramaia122-lgtm/logistica-aura") 
    except Exception as e:
        st.error(f"❌ Erro de conexão: {e}")
        return None

def gerenciar_dados(repo, acao="carregar", df_novo=None, sha=None):
    path = "dados_logistica.csv"
    try:
        if acao == "carregar":
            try:
                content = repo.get_contents(path)
                return pd.read_csv(io.StringIO(content.decoded_content.decode('utf-8'))), content.sha
            except:
                return pd.DataFrame(columns=["Data", "Motorista", "Passageiro", "Trajeto", "Valor"]), None
        else:
            csv_data = df_novo.to_csv(index=False)
            if sha: repo.update_file(path, "Sincronização", csv_data, sha)
            else: repo.create_file(path, "Início do Banco", csv_data)
            return True
    except Exception as e:
        st.error(f"⚠️ Erro nos dados: {e}")
        return None, None

# 3. TERMOS DE PRIVACIDADE (LGPD)
if 'lgpd' not in st.session_state:
    st.session_state.lgpd = False

if not st.session_state.lgpd:
    st.markdown(f'<div style="text-align: center;">{logo_html}</div>', unsafe_allow_html=True)
    st.subheader("🛡️ Termos de Privacidade Aura Apoena")
    st.info("O acesso requer a aceitação do tratamento de dados para fins logísticos.")
    if st.checkbox("Aceito os termos da LGPD e Política de Privacidade."):
        if st.button("Entrar no Sistema"):
            st.session_state.lgpd = True
            st.rerun()
    st.stop()

# 4. APLICAÇÃO PRINCIPAL
repo = conectar_github()
if repo:
    df, sha = gerenciar_dados(repo, "carregar")

    with st.sidebar:
        st.markdown(f'<div style="text-align: center; padding-bottom: 20px;">{logo_html}</div>', unsafe_allow_html=True)
        menu = st.radio("NAVEGAÇÃO", ["🏠 Dashboard", "📝 Programar", "📋 Agenda", "💰 Financeiro"])

    if menu == "🏠 Dashboard":
        st.title("Gestão Estratégica de Logística")
        st.write("Visão Geral de Pessoas e Infraestrutura.")
        c1, c2 = st.columns(2)
        c1.metric("Viagens Registradas", len(df))
        c2.metric("Custo Total", f"R$ {pd.to_numeric(df['Valor'], errors='coerce').sum():.2f}")

    elif menu == "📝 Programar":
        st.header("📝 Nova Programação")
        with st.form("add_viagem", clear_on_submit=True):
            col1, col2 = st.columns(2)
            pax = col1.text_input("Passageiro").upper()
            mot = col1.selectbox("Motorista", ["Ilson", "Antonio", "Outro"])
            tra = col2.selectbox("Trajeto", ["P. Lacerda x Cuiabá", "Interno", "Outro"])
            if st.form_submit_button("✅ SALVAR"):
                if pax:
                    nova = pd.DataFrame([{"Data": datetime.now().strftime('%d/%m/%Y'), "Motorista": mot, "Passageiro": pax, "Trajeto": tra, "Valor": 0}])
                    gerenciar_dados(repo, "salvar", pd.concat([df, nova], ignore_index=True), sha)
                    st.success("Salvo com sucesso!")
                    st.rerun()

    elif menu == "💰 Financeiro":
        st.header("💰 Controle Financeiro")
        df_edit = st.data_editor(df, use_container_width=True, num_rows="dynamic")
        if st.button("💾 ATUALIZAR"):
            if st.checkbox("Confirmar alterações estratégicas"):
                gerenciar_dados(repo, "salvar", df_edit, sha)
                st.success("Planilha sincronizada!")
                st.rerun()

    elif menu == "📋 Agenda":
        st.header("📋 Agenda de Viagens")
        st.dataframe(df, use_container_width=True)
