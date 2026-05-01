import streamlit as st
import pandas as pd
from github import Github
import io
from datetime import datetime

# 1. CONFIGURAÇÃO DE PÁGINA E ESTILO AURA
st.set_page_config(page_title="Logística Apoena", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF !important; }
    [data-testid="stSidebar"] { background-color: #002D5E !important; }
    [data-testid="stSidebar"] * { color: #FFFFFF !important; }
    h1, h2, h3, label { color: #002D5E !important; font-family: 'Open Sans', sans-serif; }
    div[data-baseweb="input"], div[data-baseweb="select"] {
        background-color: #E8E8E8 !important;
        border: 1px solid #002D5E !important;
        border-radius: 4px !important;
    }
    .stButton>button {
        background-color: #E8E8E8 !important;
        color: #002D5E !important;
        border: 2px solid #002D5E !important;
        border-radius: 6px !important;
        font-weight: bold; width: 100%;
    }
    .stButton>button:hover { background-color: #002D5E !important; color: #FFFFFF !important; }
    .logo-aura { filter: drop-shadow(0px 4px 8px rgba(0,0,0,0.5)); display: block; margin: auto; }
    </style>
    """, unsafe_allow_html=True)

# 2. FUNÇÕES DE DADOS (COM TRATAMENTO DE ERRO PARA EVITAR TELA BRANCA)
def conectar_github():
    try:
        # Tenta buscar o token nos Secrets
        if "GITHUB_TOKEN" not in st.secrets:
            st.error("❌ Erro Crítico: 'GITHUB_TOKEN' não encontrado nos Secrets do Streamlit.")
            return None
        
        token = st.secrets["GITHUB_TOKEN"]
        g = Github(token)
        # IMPORTANTE: Verifique se o nome do repositório abaixo está correto no seu GitHub
        repo = g.get_user().get_repo("logistica-aura") 
        return repo
    except Exception as e:
        st.error(f"❌ Falha ao conectar ao GitHub: {e}")
        return None

def gerenciar_dados(repo, acao="carregar", df_novo=None, sha=None):
    file_path = "dados_logistica.csv"
    try:
        if acao == "carregar":
            try:
                file_content = repo.get_contents(file_path)
                df = pd.read_csv(io.StringIO(file_content.decoded_content.decode('utf-8')))
                return df, file_content.sha
            except:
                # Se o arquivo não existir, retorna um DataFrame vazio estruturado
                return pd.DataFrame(columns=["Data", "Motorista", "Passageiro", "Trajeto", "Valor"]), None
        else:
            csv_string = df_novo.to_csv(index=False)
            if sha:
                repo.update_file(file_path, "Update Logística", csv_string, sha)
            else:
                repo.create_file(file_path, "Iniciando Banco de Dados", csv_string)
            return True
    except Exception as e:
        st.error(f"⚠️ Erro ao processar dados: {e}")
        return None, None

# 3. LÓGICA DE CONSENTIMENTO (LGPD)
if 'aceite_lgpd' not in st.session_state:
    st.session_state.aceite_lgpd = False

if not st.session_state.aceite_lgpd:
    st.markdown('<div style="text-align: center;"><img src="https://gist.githubusercontent.com/user-attachments/assets/8e0f5228-40b9-4674-9f0f-6df3d57b280c" width="180" class="logo-aura"></div>', unsafe_allow_html=True)
    st.subheader("🛡️ Termos de Privacidade e Uso")
    st.info("Para prosseguir, aceite os termos de uso de dados da Aura Apoena.")
    
    with st.expander("Leia a Política de Privacidade (LGPD)"):
        st.write("Os dados coletados são usados exclusivamente para fins de logística interna.")
    
    concordo = st.checkbox("Eu concordo com o tratamento dos dados conforme a política descrita.")
    if st.button("Acessar Sistema"):
        if concordo:
            st.session_state.aceite_lgpd = True
            st.rerun()
        else:
            st.warning("Você precisa marcar a caixa de seleção para continuar.")
    st.stop()

# 4. APLICAÇÃO PRINCIPAL (SÓ EXECUTA APÓS O ACEITE)
repo = conectar_github()

if repo is not None:
    df, sha = gerenciar_dados(repo, "carregar")
    
    with st.sidebar:
        st.markdown('<div style="text-align: center;"><img src="https://gist.githubusercontent.com/user-attachments/assets/8e0f5228-40b9-4674-9f0f-6df3d57b280c" width="180" class="logo-aura"></div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        menu = st.radio("NAVEGAÇÃO", ["🏠 Home", "📝 Programar", "📋 Agenda", "💰 Financeiro"])

    if menu == "🏠 Home":
        st.title("Bem-vinda, Yara!")
        c1, c2 = st.columns(2)
        c1.metric("Viagens Registradas", len(df))
        c2.metric("Custo Total (R$)", f"{pd.to_numeric(df['Valor'], errors='coerce').sum():.2f}")

    elif menu == "📝 Programar":
        st.header("📝 Nova Programação")
        with st.form("nova_v", clear_on_submit=True):
            pax = st.text_input("Passageiro").upper()
            mot = st.selectbox("Motorista", ["Ilson", "Antonio", "Outro"])
            tra = st.selectbox("Trajeto", ["P. Lacerda x Cuiabá", "Interno", "Outro"])
            if st.form_submit_button("✅ SALVAR"):
                if pax:
                    nova = pd.DataFrame([{"Data": datetime.now().strftime('%d/%m/%Y'), "Motorista": mot, "Passageiro": pax, "Trajeto": tra, "Valor": 0}])
                    df_final = pd.concat([df, nova], ignore_index=True)
                    gerenciar_dados(repo, "salvar", df_final, sha)
                    st.success("Dados enviados ao GitHub!")
                    st.rerun()
                else:
                    st.error("Preencha o nome do passageiro.")

    elif menu == "💰 Financeiro":
        st.header("💰 Gestão Financeira")
        df_editado = st.data_editor(df, use_container_width=True, num_rows="dynamic")
        if st.button("💾 SALVAR ALTERAÇÕES"):
            if st.checkbox("Confirmo a atualização dos dados"):
                gerenciar_dados(repo, "salvar", df_editado, sha)
                st.success("Planilha atualizada!")
                st.rerun()

    elif menu == "📋 Agenda":
        st.header("📋 Agenda de Viagens")
        st.dataframe(df, use_container_width=True)
else:
    # Se o repo for None, esta mensagem impede a tela branca
    st.warning("⚠️ O sistema não pôde carregar o menu porque a conexão com o GitHub falhou. Verifique seu Token nos Secrets.")
