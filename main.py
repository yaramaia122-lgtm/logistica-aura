import streamlit as st
import pandas as pd
from github import Github, Auth
import io
import os
from datetime import datetime, timedelta

# 1. ESTILO MODERNO (DESIGN AURA 2.0)
st.set_page_config(page_title="AURA APOENA", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #F4F7F9 !important; }
    [data-testid="stSidebar"] { background-color: #002D5E !important; }
    
    /* DESIGN DA TELA DE LOGIN */
    div[data-testid="stForm"] {
        background: #002D5E;
        padding: 30px;
        border-radius: 15px;
        border: none !important;
    }
    
    /* INPUTS BRANCOS COM TEXTO ESCURO */
    div[data-testid="stForm"] .stTextInput input {
        background-color: #FFFFFF !important;
        color: #002D5E !important;
        border-radius: 8px !important;
        height: 45px !important;
    }
    
    /* TÍTULO LOGISTICAS EM BRANCO */
    .login-title {
        color: white !important;
        text-align: center;
        letter-spacing: 4px;
        font-weight: 300;
        margin-top: -10px;
        margin-bottom: 20px;
    }

    /* BOTÃO ACESSAR SISTEMA */
    div.stButton > button {
        background-color: #FFFFFF !important;
        color: #002D5E !important;
        font-weight: 700 !important;
        border-radius: 8px !important;
        height: 48px !important;
    }

    /* AGENDA ESTILO IMAGEM */
    .obs-header {
        background-color: #E75945; color: white; text-align: center;
        padding: 10px; font-weight: 600; border-radius: 10px 10px 0 0;
    }
    .obs-row { display: flex; border: 1px solid #E0E6ED; border-top: none; background: white; }
    .obs-day { width: 140px; padding: 12px; background-color: #F8FAFC; border-right: 1px solid #E0E6ED; font-weight: 600; }
    .obs-content { flex-grow: 1; padding: 12px; color: #475569; min-height: 45px; }
</style>
""", unsafe_allow_html=True)

# 2. CONEXÃO GITHUB
@st.cache_data(ttl=5)
def carregar_dados():
    try:
        tk = st.secrets["GITHUB_TOKEN"]
        rp = Github(auth=Auth.Token(tk)).get_repo("yaramaia122-lgtm/logistica-aura")
        def ler(arq, cols):
            try:
                c = rp.get_contents(arq)
                df_l = pd.read_csv(io.StringIO(c.decoded_content.decode()))
                for cl in cols:
                    if cl not in df_l.columns: df_l[cl] = ""
                return df_l, c.sha
            except: return pd.DataFrame(columns=cols), None

        cv = ["Passageiro", "Motorista", "Data", "Trajeto", "Status", "Centro_Custo", 
              "Hotel_V", "Comb_V", "Aereo_V", "Outro_V", "Total", "Voo", "Voo_Hora", "Hotel", "Hora_Saida"]
        df_v, sh_v = ler("dados_logistica.csv", cv)
        df_u, sh_u = ler("usuarios.csv", ["Usuario", "Senha"])
        df_o, sh_o = ler("observacoes.csv", ["Data", "Observacao"])
        return df_v, sh_v, df_u, sh_u, df_o, sh_o, rp
    except: return None

res = carregar_dados()
if not res: st.stop()
df, s_v, df_u, s_u, df_o, s_o, repo = res

# 3. TELA DE LOGIN (DESIGN D11B80 MODERNO)
if 'logado' not in st.session_state:
    st.session_state['logado'] = False

if st.session_state['logado'] == False:
    st.markdown("<style>.stApp { background-color: #002D5E !important; }</style>", unsafe_allow_html=True)
    _, col_log, _ = st.columns([1, 1, 1])
    with col_log:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.image("https://raw.githubusercontent.com/yaramaia122-lgtm/logistica-aura/main/logo.png", width=300)
        st.markdown("<h2 class='login-title'>LOGISTICAS</h2>", unsafe_allow_html=True)
        with st.form("login_aura"):
            st.markdown("<p style='color:white; margin-bottom:-5px;'>Usuário</p>", unsafe_allow_html=True)
            u_txt = st.text_input("u", label_visibility="collapsed")
            st.markdown("<p style='color:white; margin-bottom:-5px;'>Senha</p>", unsafe_allow_html=True)
            p_txt = st.text_input("p", type="password", label_visibility="collapsed")
            if st.form_submit_button("ACESSAR SISTEMA"):
                valid = df_u[(df_u['Usuario'] == u_txt) & (df_u['Senha'] == p_txt)]
                if not valid.empty:
                    st.session_state['logado'] = True
                    st.rerun()
                else: st.error("Acesso negado.")
else:
    # 4. SISTEMA PRINCIPAL
    with st.sidebar:
        st.image("https://raw.githubusercontent.com/yaramaia122-lgtm/logistica-aura/main/logo.png", width=180)
        menu = st.radio("NAVEGAÇÃO", ["Agenda", "Programar", "Financeiro", "Admin"])
        if st.button("SAIR"):
            st.session_state['logado'] = False
            st.rerun()

    if menu == "Agenda":
        st.title("📅 Agenda Semanal")
        st.markdown('<div class="obs-header">OBSERVAÇÕES</div>', unsafe_allow_html=True)
        dias = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
        h = datetime.now()
        seg = h - timedelta(days=h.weekday())
        for i, n in enumerate(dias):
            dc = (seg + timedelta(days=i)).strftime('%d/%m/%Y')
            lb = (seg + timedelta(days=i)).strftime('%d/%m')
            tx = df_o[df_o['Data'] == dc]['Observacao'].values[0] if dc in df_o['Data'].values else ""
            st.markdown(f'<div class="obs-row"><div class="obs-day">{n}<br><small>{lb}</small></div>'
                        f'<div class="obs-content
