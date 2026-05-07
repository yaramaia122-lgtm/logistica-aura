import streamlit as st
import pandas as pd
from github import Github, Auth
import io
import os
from datetime import datetime, timedelta

# 1. IDENTIDADE E ESTILO (PADRÃO AURA)
APP_NAME = "AURA APOENA"
st.set_page_config(page_title=APP_NAME, layout="wide")

st.markdown(f"""
<style>
    .stApp {{ background-color: #FFFFFF !important; }}
    [data-testid="stSidebar"] {{ background-color: #002D5E !important; }}
    h1, h2, h3, label, p {{ color: #002D5E !important; font-weight: 700; }}
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] label, [data-testid="stSidebar"] span {{ color: #FFFFFF !important; }}
    
    div.stButton > button {{
        background-color: #FFFFFF !important; border: 2px solid #002D5E !important;
        border-radius: 8px !important; color: #002D5E !important;
        height: 45px !important; font-weight: 900 !important;
    }}
    
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
</style>
""", unsafe_allow_html=True)

# 2. GESTÃO DE DADOS
@st.cache_data(ttl=5)
def carregar_banco():
    try:
        tk = st.secrets["GITHUB_TOKEN"]
        rp = Github(auth=Auth.Token(tk)).get_repo("yaramaia122-lgtm/logistica-aura")
        def ler(arq, cols):
            try:
                c = rp.get_contents(arq)
                df_l = pd.read_csv(io.StringIO(c.decoded_content.decode()))
                for col in cols:
                    if col not in df_l.columns: df_l[col] = ""
                return df_l, c.sha
            except: return pd.DataFrame(columns=cols), None

        cv = ["Passageiro", "Motorista", "Data", "Trajeto", "Status", "Centro_Custo", 
              "Hotel_V", "Comb_V", "Aereo_V", "Outro_V", "Total", "Voo", "Voo_Hora", "Hotel", "Hora_Saida"]
        df_v, sh_v = ler("dados_logistica.csv", cv)
        df_u, sh_u = ler("usuarios.csv", ["Usuario", "Senha", "Perfil"])
        df_o, sh_o = ler("observacoes.csv", ["Data", "Observacao"])
        return df_v, sh_v, df_u, sh_u, df_o, sh_o, rp
    except: return None

banco = carregar_banco()
if not banco: st.error("Erro de conexão."); st.stop()
df, s_v, df_u, s_u, df_o, s_o, repo = banco

# 3. ACESSO (TELA DE LOGIN - IMAGEM D11B80)
if 'logado' not in st.session_state: st.session_state['logado'] = False

if not st.session_state['logado']:
    st.markdown("<style>.stApp { background-color: #002D5E !important; }</style>", unsafe_allow_html=True)
    _, login_col, _ = st.columns([1, 1.2, 1])
    with login_col:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.image("https://raw.githubusercontent.com/yaramaia122-lgtm/logistica-aura/main/logo.png", width=280)
        st.markdown("<h2 style='color:white; text-align:center;'>LOGISTICAS</h2>", unsafe_allow_html=True)
        with st.form("f_login"):
            u = st.text_input("usuario")
            p = st.text_input("senha", type="password")
            if st.form_submit_button("ACESSAR SISTEMA"):
                if not df_u[(df_u['Usuario'] == u) & (df_u['Senha'] == p)].empty:
                    st.session_state['logado'] = True; st.rerun()
                else: st.error("Dados incorretos.")
else:
    # 4. SISTEMA
    with st.sidebar:
        st.image("https://raw.githubusercontent.com/yaramaia122-lgtm/logistica-aura/main/logo.png", width=180)
        aba = st.radio("MENU", ["📅 Agenda", "📝 Programar", "📊 Dashboard", "⚙️ Admin"])
        if st.button("SAIR"): st.session_state['logado'] = False; st.rerun()

    if aba == "📅 Agenda":
        st.title("📅 Agenda Semanal")
        st.markdown('<div class="obs-header">Observações</div>', unsafe_allow_html=True)
        ds = ["Segunda-Feira", "Terça-Feira", "Quarta-Feira", "Quinta-Feira", "Sexta-Feira", "Sábado", "Domingo"]
        h = datetime.now()
        ini = h - timedelta(days=h.weekday())
        for i, n in enumerate(ds):
            dt = (ini + timedelta(days=i)).strftime('%d/%m/%Y')
            lb = (ini + timedelta(days=i)).strftime('%d/%m')
            tx = df_o[df_o['Data'] == dt]['Observacao'].values[0] if dt in df_o['Data'].values else ""
            st.markdown(f'<div class="obs-row"><div class="obs-day">{n}<br><small>{lb}</small></div>'
                        f'<div class="obs-content">{tx}</div></div>', unsafe_allow_html=True)
        st.markdown("---")
        f = st.date_input("Filtrar dia:", h.date())
        d = f.strftime('%d/%m/%Y')
        df_d = df[(df['Data'] == d) & (df['Status'] != "Cancelada")]
        if not df_d.empty:
            for tr in df_d['Trajeto'].unique():
                st.subheader(f"📍 {tr}")
                # Colunas conforme Imagem 5964f6
                cols = ["Passageiro", "Data", "Hora_Saida", "Voo", "Voo_Hora", "Hotel", "Motorista"]
                st.dataframe(df_d[df_d['Trajeto']==tr][cols], use_container_width=True, hide_index=True)

    elif aba == "📝 Programar":
        st.title("📝 Nova Programação")
        with st.form("f_v"):
            c1, c2 = st.columns
