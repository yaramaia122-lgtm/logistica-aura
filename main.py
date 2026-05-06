import streamlit as st
import pandas as pd
from github import Github, Auth
import io
import os
from datetime import datetime, timedelta

# 1. INTERFACE E CSS (AZUL MARINHO TRAVADO)
st.set_page_config(page_title="Aura Apoena Logistics", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #FFFFFF !important; }
    [data-testid="stSidebar"] { background-color: #002D5E !important; }
    h1, h2, h3, label, p { color: #002D5E !important; font-weight: 700; }
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] label, [data-testid="stSidebar"] span { color: #FFFFFF !important; }

    /* BOTÃO COM TEXTO AZUL MARINHO SEMPRE */
    div.stButton > button, div[data-testid="stForm"] button {
        background-color: #FFFFFF !important;
        border: 2px solid #002D5E !important;
        border-radius: 8px !important;
        height: 50px !important;
    }
    div.stButton > button p, div[data-testid="stForm"] button p {
        color: #002D5E !important;
        font-weight: 900 !important;
        font-size: 16px !important;
    }
    div.stButton > button:hover { background-color: #002D5E !important; }
    div.stButton > button:hover p { color: #FFFFFF !important; }
</style>
""", unsafe_allow_html=True)

# 2. VARIÁVEIS DE SESSÃO
if 'logado' not in st.session_state: st.session_state['logado'] = False
if 'usuario_atual' not in st.session_state: st.session_state['usuario_atual'] = ""

DIAS_SEMANA = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"]

# 3. CARREGAMENTO DE DADOS
@st.cache_data(ttl=5)
def carregar_dados():
    try:
        token = st.secrets["GITHUB_TOKEN"]
        auth = Auth.Token(token)
        g = Github(auth=auth)
        repo = g.get_repo("yaramaia122-lgtm/logistica-aura")
        
        try:
            cv = repo.get_contents("dados_logistica.csv")
            df_v = pd.read_csv(io.StringIO(cv.decoded_content.decode()))
            sha_v = cv.sha
        except:
            df_v = pd.DataFrame(columns=["Passageiro", "Motorista", "Data", "Semana", "Hora_Saida", "Trajeto", "Voo_Cia_Num", "Hora_Voo", "Data_Voo", "Local_Hotel", "Total", "Status"])
            sha_v = None

        try:
            cu = repo.get_contents("usuarios.csv")
            df_u = pd.read_csv(io.StringIO(cu.decoded_content.decode()))
            sha_u = cu.sha
        except:
            df_u = pd.DataFrame([["yara.chaves", "aura123", "Administrador"]], columns=["Usuario", "Senha", "Perfil"])
            sha_u = None

        return df_v, sha_v, df_u, sha_u, repo
    except: return pd.DataFrame(), None, pd.DataFrame(), None, None

df, sha_v, df_u, sha_u, repo = carregar_dados()

# 4. SISTEMA DE LOGIN
if not st.session_state['logado']:
    st.markdown("<style>.stApp { background-color: #002D5E !important; } h2 { color: white !important; }</style>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1.2, 1])
    with c2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.image("https://raw.githubusercontent.com/yaramaia122-lgtm/logistica-aura/main/logo.png", width=220)
        st.markdown("<h2 style='text-align: center;'>Acesso</h2>", unsafe_allow_html=True)
        with st.form("login"):
            u = st.text_input("Usuário")
            s = st.text_input("Senha", type="password")
            if st.form_submit_button("ENTRAR NO SISTEMA"):
                if not df_u.empty:
                    m = df_u[(df_u['Usuario'] == u) & (df_u['Senha'] == s)]
                    if not m.empty:
                        st.session_state['logado'] = True
                        st.session_state['usuario_atual'] = u
                        st.rerun()
                    else: st.error("Login inválido")
else:
    # 5. MENU PRINCIPAL
    with st.sidebar:
        st.image("https://raw.githubusercontent.com/yaramaia122-lgtm/logistica-aura/main/logo.png", width=180)
        menu = st.radio("MENU", ["Agenda", "Programar Viagem", "Dashboard", "Administração"])
        if st.button("SAIR"): st.session_state['logado'] = False; st.rerun()

    if menu == "Agenda":
        st.title("Agenda de Viagens")
        d_sel = st.date_input("Semana de:", datetime.now().date())
        ini = d_sel - timedelta(days=d_sel.weekday())
        fim = ini + timedelta(days=6)
        
        if not df.empty:
            df['Data_Dt'] = pd.to_datetime(df['Data'], format='%d/%m/%Y', errors='coerce').dt.date
            # Lógica corrigida para não cortar parênteses
            df_s = df[(df['Data_Dt'] >= ini) & (df['Data_Dt'] <= fim)]
            if not df_s.empty:
                for t in sorted(df_s['Trajeto'].unique()):
                    st.markdown(f"### 📍 {t}")
                    st.dataframe(df_s[df_s['Trajeto'] == t], use_container_width=True, hide_index=True)
            else: st.info("Sem viagens para este período.")

    elif menu == "Programar Viagem":
        st.title("Nova Programação")
        with st.form("f_add"):
            c1, c2 = st.columns(2)
            px = c1.text_input("Passageiro").upper()
            mt = c1.selectbox("Motorista", ["Ilson", "Antonio", "Vagno", "Cido", "Outro"])
            tj = c1.selectbox("Trecho", ["Pontes e Lacerda x Cuiabá", "Cuiabá x Pontes e Lacerda", "Interno", "Outro"])
            dt = c2.date_input("Data da Viagem")
            hs = c2.text_input("Hora de Saída")
            lh = c2.text_input("Local/Hotel")
            
            st.markdown("---")
            st.write("✈️ **Dados de Voo (Se houver)**")
            v_cia = st.text_input("Cia e Nº do Voo")
            v_hor = st.text_input("Hora do Voo")
            v_dat = st.date_input("Data do Voo", value=dt)
            
            if st.form_submit_button("SALVAR PROGRAMAÇÃO"):
                sem = DIAS_SEMANA[dt.weekday()]
                nova = pd.DataFrame([{"Passageiro": px, "Motorista": mt, "Data": dt.strftime('%d/%m/%Y'), "Semana": sem, "Trajeto": tj, "Hora_Saida": hs, "Local_Hotel": lh, "Voo_Cia_Num": v_cia, "Hora_Voo": v_hor, "Data_Voo": v_dat.strftime('%d/%m/%Y'), "Status": "Confirmada", "Total": 0.0}])
                df_f = pd.concat([df, nova], ignore_index=True)
                repo.update_file("dados_logistica.csv", "Add", df_f.to_csv(index=False), sha_v)
                st.success("Gravado!"); st.rerun()

    elif menu == "Dashboard":
        st.title("Indicadores")
        if not df.empty:
            st.metric("Total de Viagens Ativas", len(df[df["Status"] != "Cancelada"]))
            st.bar_chart(df["Trajeto"].value_counts())

    elif menu == "Administração":
        st.title("Controle Administrativo")
        df_ed = st.data_editor(df, use_container_width=True, hide_index=True)
        if st.button("SALVAR ALTERAÇÕES"):
            repo.update_file("dados_logistica.csv", "Edit", df_ed.to_csv(index=False), sha_v)
            st.rerun()
