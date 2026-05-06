import streamlit as st
import pandas as pd
from github import Github, Auth
import io
import os
from datetime import datetime, timedelta

# ==========================================================
# 1. TEMA E CSS (ESTRUTURA VISUAL E DESTRAVAMENTO DE BOTÕES)
# ==========================================================
st.set_page_config(page_title="Aura Apoena Logistics", layout="wide")

st.markdown("""
<style>
    /* Fundo geral Branco */
    .stApp { background-color: #FFFFFF !important; }
    [data-testid="stSidebar"] { background-color: #002D5E !important; }
    
    /* Tipografia Azul Marinho */
    h1, h2, h3, label, p { color: #002D5E !important; font-weight: 700; }
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] label, [data-testid="stSidebar"] span { color: #FFFFFF !important; }

    /* --- ENGENHARIA DO BOTÃO (PADRÃO YARA CORRIGIDO) --- */
    div.stButton > button {
        background-color: #FFFFFF !important;
        border: 2px solid #002D5E !important;
        border-radius: 8px !important;
        height: 50px !important;
        width: 100% !important;
    }

    /* FORÇAR COR DO TEXTO (Ignorando temas automáticos) */
    div.stButton > button p {
        color: #002D5E !important;
        font-weight: 900 !important;
        font-size: 16px !important;
        margin: 0px !important;
    }

    /* Efeito de Inversão no Hover (Seta sobre o botão) */
    div.stButton > button:hover {
        background-color: #002D5E !important;
        border-color: #002D5E !important;
    }
    div.stButton > button:hover p {
        color: #FFFFFF !important;
    }

    /* Estilo de Inputs */
    .stTextInput input, .stSelectbox div[data-baseweb="select"] { 
        background-color: #F0F7FF !important; border: 2px solid #002D5E !important; color: #002D5E !important; 
    }
    .obs-header { background-color: #E75945 !important; color: white !important; text-align: center !important; padding: 10px !important; font-weight: bold !important; border-radius: 8px 8px 0px 0px; margin-bottom: -15px; }
</style>
""", unsafe_allow_html=True)

# ==========================================================
# 2. INICIALIZAÇÃO E CARREGAMENTO (BANCO DE DADOS)
# ==========================================================
if 'logado' not in st.session_state: st.session_state['logado'] = False
if 'usuario_atual' not in st.session_state: st.session_state['usuario_atual'] = ""

DIAS_SEMANA_PT = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"]

@st.cache_data(ttl=5)
def carregar_tudo():
    try:
        token = st.secrets["GITHUB_TOKEN"]
        auth = Auth.Token(token)
        g = Github(auth=auth)
        repo = g.get_repo("yaramaia122-lgtm/logistica-aura")
        
        # Carregar Viagens
        try:
            cv = repo.get_contents("dados_logistica.csv")
            df_v = pd.read_csv(io.StringIO(cv.decoded_content.decode()))
            sha_v = cv.sha
        except:
            df_v = pd.DataFrame(columns=["Passageiro", "Motorista", "Data", "Semana", "Trajeto", "Total", "Status"])
            sha_v = None

        # Carregar Usuários
        try:
            cu = repo.get_contents("usuarios.csv")
            df_u = pd.read_csv(io.StringIO(cu.decoded_content.decode()))
            sha_u = cu.sha
        except:
            df_u = pd.DataFrame([["yara.chaves", "aura123", "Administrador"]], columns=["Usuario", "Senha", "Perfil"])
            sha_u = None

        return df_v, sha_v, df_u, sha_u, repo
    except:
        return pd.DataFrame(), None, pd.DataFrame(), None, None

df, sha_viagens, df_usr, sha_usr, repo_git = carregar_tudo()

# ==========================================================
# 3. LÓGICA DE TELAS (LOGIN / SISTEMA)
# ==========================================================
if not st.session_state['logado']:
    # Fundo Azul para a tela de Login
    st.markdown("<style>.stApp { background-color: #002D5E !important; } h2 { color: white !important; }</style>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1.2, 1])
    with c2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.image("https://raw.githubusercontent.com/yaramaia122-lgtm/logistica-aura/main/logo.png", width=220)
        st.markdown("<h2 style='text-align: center;'>Acesso Restrito</h2>", unsafe_allow_html=True)
        with st.form("form_login"):
            u = st.text_input("Usuário Corporativo")
            s = st.text_input("Senha", type="password")
            if st.form_submit_button("ENTRAR NO SISTEMA"):
                if not df_usr.empty:
                    match = df_usr[(df_usr['Usuario'] == u) & (df_usr['Senha'] == s)]
                    if not match.empty:
                        st.session_state['logado'] = True
                        st.session_state['usuario_atual'] = u
                        st.rerun()
                    else: st.error("Dados inválidos.")
else:
    # --- INTERFACE PRINCIPAL ---
    with st.sidebar:
        st.image("https://raw.githubusercontent.com/yaramaia122-lgtm/logistica-aura/main/logo.png", width=180)
        st.write(f"Conectado: **{st.session_state['usuario_atual']}**")
        menu = st.radio("NAVEGAÇÃO", ["Agenda", "Dashboard", "Programar Viagem", "Administração"])
        if st.button("ENCERRAR SESSÃO"):
            st.session_state['logado'] = False
            st.rerun()

    # --- MÓDULO: AGENDA ---
    if menu == "Agenda":
        st.title("Agenda Operacional")
        d_sel = st.date_input("Ver semana de:", datetime.now().date())
        ini = d_sel - timedelta(days=d_sel.weekday())
        fim = ini + timedelta(days=6)
        
        if not df.empty and 'Data' in df.columns:
            df['Data_Dt'] = pd.to_datetime(df['Data'], format='%d/%m/%Y', errors='coerce').dt.date
            df_s = df[(df['Data_Dt'] >= ini) & (df['Data_Dt'] <= fim)].copy()
            if not df_s.empty:
                for t in sorted(df_s['Trajeto'].unique()):
                    st.markdown(f"### 📍 {t}")
                    st.dataframe(df_s[df_s['Trajeto'] == t][["Passageiro", "Data", "Semana", "Motorista", "Status"]], use_container_width=True, hide_index=True)
            else: st.info("Nenhuma viagem programada para esta semana.")

    # --- MÓDULO: DASHBOARD (RESTAURADO) ---
    elif menu == "Dashboard":
        st.title("Painel de Indicadores")
        if not df.empty:
            c1, c2, c3 = st.columns(3)
            df_at = df[df["Status"] != "Cancelada"].copy()
            c1.metric("Total de Viagens", len(df_at))
            if 'Total' in df_at.columns:
                c2.metric("Custo Total", f"R$ {df_at['Total'].sum():,.2f}")
            c3.metric("Cancelamentos", len(df[df["Status"] == "Cancelada"]))
            
            st.markdown("---")
            col_g1, col_g2 = st.columns(2)
            with col_g1:
                st.subheader("Viagens por Trecho")
                st.bar_chart(df_at['Trajeto'].value_counts())
            with col_g2:
                st.subheader("Uso de Motoristas")
                st.bar_chart(df_at['Motorista'].value_counts())
        else: st.warning("Aguardando dados para gerar gráficos.")

    # --- MÓDULO: PROGRAMAR ---
    elif menu == "Programar Viagem":
        st.title("Nova Programação")
        with st.form("f_add"):
            c1, c2 = st.columns(2)
            px = c1.text_input("Passageiro").upper()
            mt = c1.selectbox("Motorista", ["Ilson", "Antonio", "Vagno", "Cido", "Outro"])
            tj = c1.selectbox("Trecho", ["Pontes e Lacerda x Cuiabá", "Cuiabá x Pontes e Lacerda", "Interno", "Outro"])
            dt = c2.date_input("Data")
            hs = c2.text_input("Hora Saída")
            cc = c2.text_input("Centro de Custo")
            if st.form_submit_button("GRAVAR VIAGEM"):
                sem = DIAS_SEMANA_PT[dt.weekday()]
                nova = pd.DataFrame([{"Passageiro": px, "Motorista": mt, "Data": dt.strftime('%d/%m/%Y'), "Semana": sem, "Trajeto": tj, "Status": "Confirmada", "Total": 0.0}])
                df_final = pd.concat([df, nova], ignore_index=True)
                repo_git.update_file("dados_logistica.csv", "Add", df_final.to_csv(index=False), sha_viagens)
                st.success("Programação salva com sucesso!"); st.rerun()

    # --- MÓDULO: ADMINISTRAÇÃO ---
    elif menu == "Administração":
        st.title("Controle de Dados")
        df_ed = st.data_editor(df, use_container_width=True, hide_index=True)
        if st.button("SALVAR TODAS AS ALTERAÇÕES"):
            repo_git.update_file("dados_logistica.csv", "Edit", df_ed.to_csv(index=False), sha_viagens)
            st.success("Banco de dados atualizado!"); st.rerun()
