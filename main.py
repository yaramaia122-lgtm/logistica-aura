import streamlit as st
import pandas as pd
from github import Github, Auth
import io
import os
from datetime import datetime, timedelta

# 1. CONFIGURAÇÕES E IDENTIDADE VISUAL
APP_NAME = "AURA APOENA LOGISTICS"
st.set_page_config(page_title=APP_NAME, layout="wide")

st.markdown(f"""
<style>
    .stApp {{ background-color: #FFFFFF !important; }}
    [data-testid="stSidebar"] {{ background-color: #002D5E !important; }}
    h1, h2, h3, label, p {{ color: #002D5E !important; font-weight: 700; }}
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] label, [data-testid="stSidebar"] span {{ color: #FFFFFF !important; }}
    
    /* BOTÃO PADRÃO BRANCO COM LETRA AZUL MARINHO */
    div.stButton > button, div[data-testid="stForm"] button {{
        background-color: #FFFFFF !important;
        border: 2px solid #002D5E !important;
        border-radius: 8px !important;
        color: #002D5E !important;
        height: 45px !important;
        width: 100% !important;
        font-weight: 900 !important;
    }}
    
    /* CABEÇALHO DE OBSERVAÇÕES VERMELHO (PADRÃO IMAGEM) */
    .obs-header {{
        background-color: #E75945; color: white; text-align: center;
        padding: 10px; font-weight: bold; border: 1px solid #ddd;
        border-radius: 5px 5px 0 0;
    }}
    .obs-row {{ display: flex; border: 1px solid #ddd; border-top: none; }}
    .obs-day {{
        width: 140px; padding: 12px; background-color: #f8f9fa;
        border-right: 1px solid #ddd; font-weight: bold; font-size: 14px;
    }}
    .obs-content {{ flex-grow: 1; padding: 12px; color: #333; min-height: 50px; }}
</style>
""", unsafe_allow_html=True)

# 2. CONEXÃO COM GITHUB (BANCO DE DADOS)
@st.cache_data(ttl=5)
def conectar():
    try:
        token = st.secrets["GITHUB_TOKEN"]
        repo = Github(auth=Auth.Token(token)).get_repo("yaramaia122-lgtm/logistica-aura")
        
        def carregar(arquivo, colunas):
            try:
                conteudo = repo.get_contents(arquivo)
                df_l = pd.read_csv(io.StringIO(conteudo.decoded_content.decode()))
                return df_l, conteudo.sha
            except:
                return pd.DataFrame(columns=colunas), None

        cols_v = ["Passageiro", "Motorista", "Data", "Trajeto", "Status", "Centro_Custo", 
                  "Hotel_V", "Comb_V", "Aereo_V", "Outro_V", "Total", "Voo", "Voo_Hora", "Hotel"]
        
        df_v, sha_v = carregar("dados_logistica.csv", cols_v)
        df_u, sha_u = carregar("usuarios.csv", ["Usuario", "Senha", "Perfil"])
        df_o, sha_o = carregar("observacoes.csv", ["Data", "Observacao"])
        
        return df_v, sha_v, df_u, sha_u, df_o, sha_o, repo
    except:
        return None

banco = conectar()
if not banco:
    st.error("Erro de conexão com o banco de dados.")
    st.stop()

df, s_v, df_u, s_u, df_o, s_o, repo = banco

# 3. LÓGICA DE LOGIN
if 'logado' not in st.session_state:
    st.session_state['logado'] = False

if not st.session_state['logado']:
    st.markdown("<style>.stApp { background-color: #002D5E !important; }</style>", unsafe_allow_html=True)
    _, login_col, _ = st.columns([1, 1.2, 1])
    with login_col:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.image("https://raw.githubusercontent.com/yaramaia122-lgtm/logistica-aura/main/logo.png", width=250)
        st.markdown(f"<h2 style='color:white; text-align:center;'>{APP_NAME}</h2>", unsafe_allow_html=True)
        with st.form("form_login"):
            user_input = st.text_input("Usuário")
            pass_input = st.text_input("Senha", type="password")
            if st.form_submit_button("ACESSAR SISTEMA"):
                if not df_u[(df_u['Usuario'] == user_input) & (df_u['Senha'] == pass_input)].empty:
                    st.session_state['logado'] = True
                    st.rerun()
                else:
                    st.error("Credenciais inválidas.")
else:
    # 4. PAINEL PRINCIPAL
    with st.sidebar:
        st.image("https://raw.githubusercontent.com/yaramaia122-lgtm/logistica-aura/main/logo.png", width=180)
        st.markdown("---")
        aba = st.radio("MENU PRINCIPAL", ["📅 Agenda", "📝 Programar", "📊 Dashboard", "⚙️ Admin"])
        if st.button("SAIR DO SISTEMA"):
            st.session_state['logado'] = False
            st.rerun()

    # --- ABA: AGENDA ---
    if aba == "📅 Agenda":
        st.title("Agenda Semanal de Logística")
        
        # Bloco de Observações (Estilo Imagem 59c22f)
        st.markdown('<div class="obs-header">OBSERVAÇÕES DA SEMANA</div>', unsafe_allow_html=True)
        dias = ["Segunda-Feira", "Terça-Feira", "Quarta-Feira", "Quinta-Feira", "Sexta-Feira", "Sábado", "Domingo"]
        hoje = datetime.now()
        segunda = hoje - timedelta(
