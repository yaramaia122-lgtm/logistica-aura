import streamlit as st
import pandas as pd
from github import Github, Auth
import io
import os
from datetime import datetime, timedelta

# ==========================================================
# 0. INICIALIZAÇÃO DE SESSÃO E SEGURANÇA
# ==========================================================
if 'logado' not in st.session_state:
    st.session_state['logado'] = False
if 'usuario_atual' not in st.session_state:
    st.session_state['usuario_atual'] = ""
if 'perfil' not in st.session_state:
    st.session_state['perfil'] = ""
if 'precisa_trocar_senha' not in st.session_state:
    st.session_state['precisa_trocar_senha'] = False
if 'usuario_troca' not in st.session_state:
    st.session_state['usuario_troca'] = ""

MESES_PT = {1:'jan', 2:'fev', 3:'mar', 4:'abr', 5:'mai', 6:'jun', 7:'jul', 8:'ago', 9:'set', 10:'out', 11:'nov', 12:'dez'}
DIAS_SEMANA_PT = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"]

# ==========================================================
# 1. TEMA E CSS (REVISÃO TÉCNICA DOS BOTÕES)
# ==========================================================
def forcar_tema_claro():
    try:
        os.makedirs(".streamlit", exist_ok=True)
        arquivo = ".streamlit/config.toml"
        conteudo = "[theme]\nbase='light'\nprimaryColor='#002D5E'\n"
        if not os.path.exists(arquivo):
            with open(arquivo, "w") as f: f.write(conteudo)
    except:
        pass

st.set_page_config(page_title="Aura Apoena Logistics", layout="wide")
forcar_tema_claro()

st.markdown("""
<style>
    /* Fundo Branco Geral */
    .stApp { background-color: #FFFFFF !important; }
    [data-testid="stSidebar"] { background-color: #002D5E !important; }
    
    /* Textos em Azul Marinho */
    h1, h2, h3, label, .stMarkdown p { color: #002D5E !important; font-weight: 700 !important; }
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] label, [data-testid="stSidebar"] span { color: #FFFFFF !important; }

    /* Estilo dos Botões - PADRÃO YARA */
    div.stButton > button {
        background-color: #FFFFFF !important;
        border: 2px solid #002D5E !important;
        border-radius: 8px !important;
        width: 100% !important;
        height: 50px !important;
    }
    
    /* Texto do Botão em Azul Marinho (Estado Normal) */
    div.stButton > button p {
        color: #002D5E !important;
        font-weight: 900 !important;
        font-size: 16px !important;
    }

    /* Texto do Botão em Branco (Quando a seta está em cima) */
    div.stButton > button:hover {
        background-color: #002D5E !important;
        border: 2px solid #002D5E !important;
    }
    div.stButton > button:hover p {
        color: #FFFFFF !important;
    }
    
    /* Inputs */
    .stTextInput input, .stSelectbox div[data-baseweb="select"], .stDateInput input, .stNumberInput input { 
        background-color: #F0F7FF !important; border: 2px solid #002D5E !important; border-radius: 6px !important; color: #002D5E !important; 
    }

    .obs-header { background-color: #E75945 !important; color: white !important; text-align: center !important; padding: 10px !important; font-weight: bold !important; border-radius: 8px 8px 0px 0px; margin-bottom: -15px; }
</style>
""", unsafe_allow_html=True)

# ==========================================================
# 2. MOTOR DE BANCO DE DADOS
# ==========================================================
@st.cache_data(ttl=5)
def carregar_bancos():
    cols_v = ["Passageiro", "Motorista", "Data", "Semana", "Hora_Saida", "Trajeto", "Voo_Cia_Num", "Hora_Voo", "Data_Voo", "Local_Hotel", "Centro de Custo", "Status", "Hotel_Valor", "Combustivel_Valor", "Aereo_Valor", "Outros_Valor", "Total", "Usuario_Criador"]
    cols_u = ["Usuario", "Senha", "Perfil", "Status", "Primeiro_Acesso"]
    try:
        token = st.secrets["GITHUB_TOKEN"]
        auth = Auth.Token(token)
        g = Github(auth=auth)
        repo = g.get_repo("yaramaia122-lgtm/logistica-aura")
        
        # Carregar Viagens
        try:
            cont_v = repo.get_contents("dados_logistica.csv")
            df_v = pd.read_csv(io.StringIO(cont_v.decoded_content.decode()))
            sha_v = cont_v.sha
            for c in cols_v:
                if c not in df_v.columns: df_v[c] = 0.0 if "_Valor" in c else ""
        except:
            df_v = pd.DataFrame(columns=cols_v); sha_v = None

        # Carregar Usuários
        try:
            cont_u = repo.get_contents("usuarios.csv")
            df_u = pd.read_csv(io.StringIO(cont_u.decoded_content.decode()))
            sha_u = cont_u.sha
        except:
            df_u = pd.DataFrame([["yara.chaves", "aura123", "Administrador", "Ativo", "Sim"]], columns=cols_u)
            repo.create_file("usuarios.csv", "Init", df_u.to_csv(index=False))
            sha_u = repo.get_contents("usuarios.csv").sha

        # Carregar Observações
        try:
            cont_o = repo.get_contents("observacoes.csv")
            df_o = pd.read_csv(io.StringIO(cont_o.decoded_content.decode()))
            sha_o = cont_o.sha
        except:
            df_o = pd.DataFrame(columns=["Data", "Observacao"]); sha_o = None

        return df_v, sha_v, df_u, sha_u, df_o, sha_o, repo
    except:
        return pd.DataFrame(), None, pd.DataFrame(), None, pd.DataFrame(), None, None

df, sha_viagens, df_usuarios, sha_usuarios, df_obs, sha_obs, repo = carregar_bancos()

# ==========================================================
# 3. TELAS DE ACESSO
# ==========================================================
if not st.session_state['logado']:
    st.markdown("""<style>.stApp { background-color: #002D5E !important; } h2, label, p { color: white !important; }</style>""", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.image("https://raw.githubusercontent.com/yaramaia122-lgtm/logistica-aura/main/logo.png", width=220)
        
        if st.session_state['precisa_trocar_senha']:
            with st.form("f_pwd"):
                n = st.text_input("Nova Senha", type="password")
                c = st.text_input("Confirme", type="password")
                if st.form_submit_button("SALVAR"):
                    idx = df_usuarios.index[df_usuarios['Usuario'] == st.session_state['usuario_troca']].tolist()[0]
                    df_usuarios.at[idx, 'Senha'], df_usuarios.at[idx, 'Primeiro_Acesso'] = n, 'Nao'
                    repo.update_file("usuarios.csv", "Pwd Upd", df_usuarios.to_csv(index=False), sha_usuarios)
                    st.session_state['precisa_trocar_senha'] = False
                    st.rerun()
        else:
            with st.form("f_login"):
                u = st.text_input("Usuário Corporativo")
                s = st.text_input("Senha", type="password")
                if st.form_submit_button("ENTRAR NO SISTEMA"):
                    u_db = df_usuarios[(df_usuarios['Usuario'] == u) & (df_usuarios['Senha'] == s)]
                    if not u_db.empty:
                        if u_db.iloc[0]['Primeiro_Acesso'] == 'Sim':
                            st.session_state['precisa_trocar_senha'], st.session_state['usuario_troca'] = True, u
                            st.rerun()
                        else:
                            st.session_state['logado'], st.session_state['usuario_atual'], st.session_state['perfil'] = True, u, u_db.iloc[0]['Perfil']
                            st.rerun()
                    else:
                        st.error("Dados incorretos.")

# ==========================================================
# 4. APP PRINCIPAL
# ==========================================================
else:
    with st.sidebar:
        st.image("https://raw.githubusercontent.com/yaramaia122-lgtm/logistica-aura/main/logo.png", width=180)
        st.write(f"Usuário: **{st.session_state['usuario_atual']}**")
        menu = st.radio("MENU", ["Agenda", "Programar Viagem", "Dashboard", "Administração"])
