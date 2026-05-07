import streamlit as st
import pandas as pd
from github import Github, Auth
import io
import os
from datetime import datetime, timedelta

# ==========================================================
# 1. IDENTIDADE VISUAL (FORÇANDO O DESIGN DA IMAGEM D11B80)
# ==========================================================
APP_NAME = "AURA APOENA"
st.set_page_config(page_title=APP_NAME, layout="wide")

# CSS para forçar o fundo azul escuro na tela de login e os campos brancos
st.markdown(f"""
<style>
    /* Estilo para a tela de Login (Fundo Azul Marinho) */
    .login-bg {{
        background-color: #002D5E;
        position: fixed;
        top: 0; left: 0; width: 100%; height: 100%;
        display: flex; flex-direction: column; align-items: center; justify-content: center;
        z-index: 999;
    }}
    
    /* Configuração dos campos de entrada (Brancos conforme exemplo) */
    div[data-testid="stForm"] .stTextInput input {{
        background-color: #FFFFFF !important;
        color: #002D5E !important;
        border-radius: 5px !important;
        border: 1px solid #FFFFFF !important;
        height: 45px !important;
    }}
    
    /* Botão ACESSAR SISTEMA */
    div.stButton > button {{
        background-color: #FFFFFF !important;
        color: #002D5E !important;
        font-weight: 900 !important;
        border-radius: 8px !important;
        border: none !important;
        width: 100% !important;
        height: 50px !important;
        text-transform: uppercase;
    }}

    /* Estilo da Agenda (Cabeçalho Vermelho) */
    .obs-header {{
        background-color: #E75945; color: white; text-align: center;
        padding: 10px; font-weight: bold; border-radius: 5px 5px 0 0;
    }}
    .obs-row {{ display: flex; border: 1px solid #ddd; border-top: none; }}
    .obs-day {{
        width: 140px; padding: 12px; background-color: #f8f9fa;
        border-right: 1px solid #ddd; font-weight: bold;
    }}
    .obs-content {{ flex-grow: 1; padding: 12px; color: #333; min-height: 45px; }}

    /* Sidebar */
    [data-testid="stSidebar"] {{ background-color: #002D5E !important; }}
    [data-testid="stSidebar"] * {{ color: white !important; }}
</style>
""", unsafe_allow_html=True)

# ==========================================================
# 2. CONEXÃO COM O BANCO DE DADOS (GITHUB)
# ==========================================================
@st.cache_data(ttl=5)
def carregar_banco():
    try:
        tk = st.secrets["GITHUB_TOKEN"]
        rp = Github(auth=Auth.Token(tk)).get_repo("yaramaia122-lgtm/logistica-aura")
        
        def ler(arq, cols):
            try:
                c = rp.get_contents(arq)
                df_l = pd.read_csv(io.StringIO(c.decoded_content.decode()))
                # Blindagem contra KeyError: garante que todas as colunas existam
                for col in cols:
                    if col not in df_l.columns: df_l[col] = ""
                return df_l, c.sha
            except: return pd.DataFrame(columns=cols), None

        # Definição rigorosa das colunas
        cols_v = ["Passageiro", "Motorista", "Data", "Trajeto", "Status", "Centro_Custo", 
                  "Hotel_V", "Comb_V", "Aereo_V", "Outro_V", "Total", "Voo", "Voo_Hora", "Hotel", "Hora_Saida"]
        
        df_v, sh_v = ler("dados_logistica.csv", cols_v)
        df_u, sh_u = ler("usuarios.csv", ["Usuario", "Senha", "Perfil"])
        df_o, sh_o = ler("observacoes.csv", ["Data", "Observacao"])
        
        return df_v, sh_v, df_u, sh_u, df_o, sh_o, rp
    except:
        return None

banco = carregar_banco()
if not banco:
    st.error("Erro técnico: Verifique o GITHUB_TOKEN.")
    st.stop()
df, s_v, df_u, s_u, df_o, s_o, repo = banco

# ==========================================================
# 3. TELA DE LOGIN (DESIGN FIEL À IMAGEM D11B80)
# ==========================================================
if 'logado' not in st.session_state:
    st.session_state['logado'] = False

if not st.session_state['logado']:
    # Aplicando fundo azul marinho na página toda
    st.markdown("<style>.stApp { background-color: #002D5E !important; }</style>", unsafe_allow_html=True)
    
    _, col_login, _ = st.columns([1, 1.2, 1])
    with col_login:
        st.markdown("<br><br>", unsafe_allow_html=True)
        # Logo Centralizada
        st.image("https://raw.githubusercontent.com/yaramaia122-lgtm/logistica-aura/main/logo.png", width=300)
        st.markdown("<h2 style='color:white; text-align:center; letter-spacing: 5px;'>LOGISTICAS</h2>", unsafe_allow_html=True)
        
        with st.form("form_acesso"):
            u = st.text_input("usuario")
            p = st.text_input("senha", type="password")
            st.markdown("<p style='color:white; text-align:right; font-size:12px;'>Mostrar senha</p>", unsafe_allow_html=True)
            
            if st.form_submit_button("ACESSAR SISTEMA"):
                user_match = df_u[(df_u['Usuario'] == u) & (df_u['Senha'] == p)]
                if not user_match.empty:
                    st.session_state['logado'] = True
                    st.rerun()
                else:
                    st.error("Usuário ou senha incorretos.")

# ==========================================================
# 4. SISTEMA PRINCIPAL (MÓDULOS)
# ==========================================================
else:
    with st.sidebar:
        st.image("https://raw.githubusercontent.com/yaramaia122-lgtm/logistica-aura/main/logo.png", width=180)
        st.markdown("---")
        aba = st.radio("NAVEGAÇÃO", ["📅 Agenda", "📝 Programar", "📊 Dashboard", "⚙️ Admin"])
        if st.button("SAIR"):
            st.session_state['logado'] = False
            st.rerun()

    # --- MÓDULO AGENDA (ESTILO IMAGEM 59C22F) ---
    if aba == "📅 Agenda
