import streamlit as st
import pandas as pd
from github import Github, Auth
import io
import os
from datetime import datetime, timedelta

# ==========================================================
# 1. CONFIGURAÇÕES E ESTILO (AZUL MARINHO E BRANCO)
# ==========================================================
APP_NAME = "AURA APOENA LOGISTICS"
st.set_page_config(page_title=APP_NAME, layout="wide")

st.markdown(f"""
<style>
    .stApp {{ background-color: #FFFFFF !important; }}
    [data-testid="stSidebar"] {{ background-color: #002D5E !important; }}
    h1, h2, h3, label, p {{ color: #002D5E !important; font-weight: 700; }}
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] label, [data-testid="stSidebar"] span {{ color: #FFFFFF !important; }}
    
    div.stButton > button, div[data-testid="stForm"] button {{
        background-color: #FFFFFF !important;
        border: 2px solid #002D5E !important;
        border-radius: 8px !important;
        color: #002D5E !important;
        height: 45px !important;
        width: 100% !important;
        font-weight: 900 !important;
    }}
    
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

# ==========================================================
# 2. CONEXÃO COM O BANCO DE DADOS (GITHUB)
# ==========================================================
@st.cache_data(ttl=5)
def conectar_banco():
    try:
        token = st.secrets["GITHUB_TOKEN"]
        repo = Github(auth=Auth.Token(token)).get_repo("yaramaia122-lgtm/logistica-aura")
        
        def carregar_csv(arquivo, colunas):
            try:
                conteudo = repo.get_contents(arquivo)
                return pd.read_csv(io.StringIO(conteudo.decoded_content.decode())), conteudo.sha
            except:
                return pd.DataFrame(columns=colunas), None

        cols_v = ["Passageiro", "Motorista", "Data", "Trajeto", "Status", "Centro_Custo", 
                  "Hotel_V", "Comb_V", "Aereo_V", "Outro_V", "Total", "Voo", "Voo_Hora", "Hotel"]
        
        df_v, sha_v = carregar_csv("dados_logistica.csv", cols_v)
        df_u, sha_u = carregar_csv("usuarios.csv", ["Usuario", "Senha", "Perfil"])
        df_o, sha_o = carregar_csv("observacoes.csv", ["Data", "Observacao"])
        
        return df_v, sha_v, df_u, sha_u, df_o, sha_o, repo
    except:
        return None

banco = conectar_banco()
if not banco:
    st.error("Erro de conexão. Verifique o GITHUB_TOKEN.")
    st.stop()

df, s_v, df_u, s_u, df_o, s_o, repo = banco

# ==========================================================
# 3. ACESSO AO SISTEMA (LOGIN)
# ==========================================================
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
                    st.error("Credenciais incorretas.")
else:
    # ==========================================================
    # 4. PAINEL PRINCIPAL
    # ==========================================================
    with st.sidebar:
        st.image("https://raw.githubusercontent.com/yaramaia122-lgtm/logistica-aura/main/logo.png", width=180)
        st.markdown("---")
        aba = st.radio("MENU", ["📅 Agenda", "📝 Programar", "📊 Dashboard", "⚙️ Admin"])
        if st.button("ENCERRAR SESSÃO"):
            st.session_state['logado'] = False
            st.rerun()

    # --- AGENDA (VISUAL IMAGEM 59C22F) ---
    if aba == "📅 Agenda":
        st.title("📅 Agenda Semanal")
        st.markdown('<div class="obs-header">OBSERVAÇÕES DA SEMANA</div>', unsafe_allow_html=True)
        
        dias_nome = ["Segunda-Feira", "Terça-Feira", "Quarta-Feira", "Quinta-Feira", "Sexta-Feira", "Sábado", "Domingo"]
        hoje = datetime.now()
        # Cálculo seguro para o início da semana
        segunda = hoje - timedelta(days=hoje.weekday())
        
        for i, nome_dia in enumerate(dias_nome):
            data_corrente = segunda + timedelta(days=i)
            data_str = data_corrente.strftime('%d/%m/%Y')
            data_label = data_corrente.strftime('%d/%m')
            
            txt_obs = ""
            if not df_o.empty:
                match = df_o[df_o['Data'] == data_str]
                if not match.empty:
                    txt_obs = match.iloc[0]['Observacao']
            
            st.markdown(f"""
            <div class="obs-row">
                <div class="obs-day">{nome_dia}<br><small>{data_label}</small></div>
                <div class="obs-content">{txt_obs}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        filtro_data = st.date_input("Filtrar viagens por dia:", hoje.date())
        data_busca = filtro_data.strftime('%d/%m/%Y')
        
        df_dia = df[(df['Data'] == data_busca) & (df['Status'] != "Cancelada")]
        if not df_dia.empty:
            for trecho in df_dia['Trajeto'].unique():
                st.subheader(f"📍 {trecho}")
                st.dataframe(df_dia[df_dia['Trajeto'] == trecho][["Passageiro", "Motorista", "Centro_Custo", "Voo", "Voo_Hora", "Hotel"]], 
                             use_container_width=True, hide_index=True)
        else:
            st.info(f"Sem viagens ativas para {data_busca}")

    # --- PROGRAMAR ---
    elif aba == "📝 Programar":
        st.title("📝 Nova Programação")
        with st.form("form_viagem"):
            c1, c2 = st.columns(2)
            pax = c1.text_input("Passageiro").upper()
            mot = c1.selectbox("Motorista", ["Ilson", "Antonio", "Vagno", "Cido", "Outro"])
            trj = c1.selectbox("Trecho", ["Pontes e Lacerda x Cuiabá", "Cuiabá x Pontes e Lacerda", "Interno"])
            ccc = c1.text_input("Centro de Custo")
            
            dat = c2.date_input("Data")
            hsa = c2.text_input("Hora Saída")
            htl = c2.text_input("Hotel/Destino")
            
            st.markdown("### Valores Previstos")
            f1, f2, f3, f4 = st.columns(4)
            vh = f1.number_input("Hotel", 0.0)
            vc = f2.number_input("Comb
