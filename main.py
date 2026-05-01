import streamlit as st
import pandas as pd
from github import Github
import io
from datetime import datetime

# 1. IDENTIDADE VISUAL AURA (MODERNA E PROFISSIONAL)
st.set_page_config(page_title="Logística Aura", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF !important; }
    [data-testid="stSidebar"] { background-color: #002D5E !important; }
    [data-testid="stSidebar"] * { color: #FFFFFF !important; }
    h1, h2, h3, label { color: #002D5E !important; font-family: 'Segoe UI', sans-serif; }
    
    /* Campos de entrada e botões em Cinza e Azul */
    div[data-baseweb="input"], div[data-baseweb="select"] {
        background-color: #E8E8E8 !important;
        border: 1px solid #002D5E !important;
        border-radius: 4px !important;
    }
    .stButton>button {
        background-color: #E8E8E8 !important;
        color: #002D5E !important;
        border: 2px solid #002D5E !important;
        font-weight: bold; width: 100%;
    }
    .stButton>button:hover { background-color: #002D5E !important; color: #FFFFFF !important; }
    .logo-aura { filter: drop-shadow(0px 4px 8px rgba(0,0,0,0.5)); display: block; margin: auto; }
    </style>
    """, unsafe_allow_html=True)

# 2. CONEXÃO COM O REPOSITÓRIO ESPECÍFICO
def conectar_github():
    try:
        if "GITHUB_TOKEN" not in st.secrets:
            st.error("❌ Erro: 'GITHUB_TOKEN' não configurado nos Secrets.")
            return None
        
        g = Github(st.secrets["GITHUB_TOKEN"])
        # Usando o caminho completo do repositório informado
        repo = g.get_repo("yaramaia122-lgtm/logistica-aura") 
        return repo
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
            if sha:
                repo.update_file(path, "Sync Logística", csv_data, sha)
            else:
                repo.create_file(path, "Init DB", csv_data)
            return True
    except Exception as e:
        st.error(f"⚠️ Erro nos dados: {e}")
        return None, None

# 3. ESCUDO JURÍDICO E LGPD
if 'lgpd' not in st.session_state:
    st.session_state.lgpd = False

if not st.session_state.lgpd:
    st.markdown('<div style="text-align: center;"><img src="https://gist.githubusercontent.com/user-attachments/assets/8e0f5228-40b9-4674-9f0f-6df3d57b280c" width="180" class="logo-aura"></div>', unsafe_allow_html=True)
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
        st.markdown('<div class="logo-container"><img src="https://gist.githubusercontent.com/user-attachments/assets/8e0f5228-40b9-4674-9f0f-6df3d57b280c" width="180" class="logo-aura"></div>', unsafe_allow_html=True)
        menu = st.radio("NAVEGAÇÃO", ["🏠 Dashboard", "📝 Programar", "📋 Agenda", "💰 Financeiro"])

    if menu == "🏠 Dashboard":
        st.title("Logística Aura Minerals")
        st.write("Visão geral estratégica de pessoas e frotas.") # Alinhado ao foco em Gestão de Pessoas
        c1, c2 = st.columns(2)
        c1.metric("Total de Viagens", len(df))
        c2.metric("Custo Acumulado", f"R$ {pd.to_numeric(df['Valor'], errors='coerce').sum():.2f}")

    elif menu == "📝 Programar":
        st.header("📝 Nova Programação")
        with st.form("add_viagem", clear_on_submit=True):
            pax = st.text_input("Passageiro").upper()
            mot = st.selectbox("Motorista", ["Ilson", "Antonio", "Outro"])
            tra = st.selectbox("Trajeto", ["P. Lacerda x Cuiabá", "Interno", "Outro"])
            if st.form_submit_button("✅ SALVAR"):
                if pax:
                    nova = pd.DataFrame([{"Data": datetime.now().strftime('%d/%m/%Y'), "Motorista": mot, "Passageiro": pax, "Trajeto": tra, "Valor": 0}])
                    df_res = pd.concat([df, nova], ignore_index=True)
                    gerenciar_dados(repo, "salvar", df_res, sha)
                    st.success("Registrado no GitHub!")
                    st.rerun()

    elif menu == "💰 Financeiro":
        st.header("💰 Controle de Custos")
        df_edit = st.data_editor(df, use_container_width=True, num_rows="dynamic")
        if st.button("💾 ATUALIZAR PLANILHA"):
            if st.checkbox("Confirmar alterações"):
                gerenciar_dados(repo, "salvar", df_edit, sha)
                st.success("Dados atualizados!")
                st.rerun()

    elif menu == "📋 Agenda":
        st.header("📋 Agenda de Viagens")
        st.dataframe(df, use_container_width=True)
