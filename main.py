import streamlit as st
import pandas as pd
from github import Github, Auth
import io
from datetime import datetime, timedelta

# 1. CONFIGURAÇÕES VISUAIS
st.set_page_config(page_title="Aura Apoena Logistics", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #FFFFFF !important; }
    [data-testid="stSidebar"] { background-color: #002D5E !important; }
    h1, h2, h3, label, p { color: #002D5E !important; font-weight: 700; }
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] label, [data-testid="stSidebar"] span { color: #FFFFFF !important; }
    div.stButton > button, div[data-testid="stForm"] button {
        background-color: #FFFFFF !important; border: 2px solid #002D5E !important;
        border-radius: 8px !important; height: 45px !important; width: 100% !important;
    }
    div.stButton > button p, div[data-testid="stForm"] button p {
        color: #002D5E !important; font-weight: 900;
    }
    .obs-card { background-color: #E75945 !important; color: white !important; padding: 15px; border-radius: 8px; margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

# 2. FUNÇÕES DE BANCO DE DADOS
@st.cache_data(ttl=5)
def carregar_dados():
    try:
        token = st.secrets["GITHUB_TOKEN"]
        repo = Github(auth=Auth.Token(token)).get_repo("yaramaia122-lgtm/logistica-aura")
        
        def get_df(file, cols):
            try:
                c = repo.get_contents(file)
                return pd.read_csv(io.StringIO(c.decoded_content.decode())), c.sha
            except: return pd.DataFrame(columns=cols), None

        df_v, sha_v = get_df("dados_logistica.csv", ["Passageiro","Motorista","Data","Semana","Trajeto","Status","Hotel_Valor","Combustivel_Valor","Aereo_Valor","Outros_Valor","Total","Voo_Cia_Num","Hora_Voo","Data_Voo","Local_Hotel"])
        df_u, sha_u = get_df("usuarios.csv", ["Usuario","Senha","Perfil"])
        df_o, sha_o = get_df("observacoes.csv", ["Data","Observacao"])
        
        return df_v, sha_v, df_u, sha_u, df_o, sha_o, repo
    except: return None

dados = carregar_dados()
if dados:
    df, sha_v, df_u, sha_u, df_o, sha_o, repo = dados
else:
    st.error("Erro de conexão com GitHub")
    st.stop()

# 3. LOGIN
if 'logado' not in st.session_state: st.session_state['logado'] = False

if not st.session_state['logado']:
    st.markdown("<style>.stApp { background-color: #002D5E !important; }</style>", unsafe_allow_html=True)
    with st.form("login"):
        st.markdown("<h2 style='color:white; text-align:center;'>AURA LOGISTICS</h2>", unsafe_allow_html=True)
        u = st.text_input("Usuário")
        s = st.text_input("Senha", type="password")
        if st.form_submit_button("ENTRAR NO SISTEMA"):
            if not df_u[(df_u['Usuario']==u) & (df_u['Senha']==s)].empty:
                st.session_state['logado'] = True
                st.rerun()
else:
    # 4. MENU
    menu = st.sidebar.radio("NAVEGAÇÃO", ["Agenda", "Programar Viagem", "Dashboard", "Administração"])
    if st.sidebar.button("SAIR"): st.session_state['logado'] = False; st.rerun()

    # --- AGENDA ---
    if menu == "Agenda":
        st.title("📅 Agenda Operacional")
        d_sel = st.date_input("Filtrar Data:", datetime.now().date())
        
        # Bloco de Observações (O que você achou legal!)
        obs_dia = df_o[df_o['Data'] == d_sel.strftime('%d/%m/%Y')]
        if not obs_dia.empty:
            for o in obs_dia['Observacao']:
                st.markdown(f"<div class='obs-card'>⚠️ <b>OBSERVAÇÃO DO DIA:</b><br>{o}</div>", unsafe_allow_html=True)
        
        # Listagem de Viagens (Sem as canceladas)
        if not df.empty:
            df['Dt_Obj'] = pd.to_datetime(df['Data'], format='%d/%m/%Y', errors='coerce').dt.date
            df_active = df[(df['Dt_Obj'] == d_sel) & (df['Status'] != "Cancelada")]
            if not df_active.empty:
                for t in sorted(df_active['Trajeto'].unique()):
                    st.subheader(f"📍 {t}")
                    st.dataframe(df_active[df_active['Trajeto']==t], use_container_width=True, hide_index=True)
            else: st.info("Nenhuma viagem ativa para hoje.")

    # --- PROGRAMAR ---
    elif menu == "Programar Viagem":
        st.title("📝 Nova Programação")
        with st.form("programar"):
            c1, c2 = st.columns(2)
            px = c1.text_input("Passageiro").upper()
            mt = c1.selectbox("Motorista", ["Ilson", "Antonio", "Vagno", "Cido", "Terceiro"])
            tj = c1.selectbox("Trecho", ["Pontes e Lacerda x Cuiabá", "Cuiabá x Pontes e Lacerda", "Interno"])
            dt = c2.date_input("Data")
            hs = c2.text_input("Hora Saída")
            lh = c2.text_input("Hotel / Destino")
            
            st.markdown("### 💰 Valores Previstos")
            v1, v2, v3, v4 = st.columns(4)
            h_v = v1.number_input("Hotel (R$)", 0.0)
            c_v = v2.number_input("Combustível (R$)", 0.0)
            a_v = v3.number_input("Aéreo (R$)", 0.0)
