import streamlit as st
import pandas as pd
from github import Github
import io
from datetime import datetime

# 1. CONFIGURAÇÃO E IDENTIDADE VISUAL (AURA MINERALS)
st.set_page_config(page_title="Logística Apoena", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF !important; }
    [data-testid="stSidebar"] { background-color: #002D5E !important; }
    [data-testid="stSidebar"] * { color: #FFFFFF !important; }
    h1, h2, h3, label { color: #002D5E !important; font-family: 'Open Sans', sans-serif; }
    
    /* Inputs Cinza e Alinhados */
    div[data-baseweb="input"], div[data-baseweb="select"] {
        background-color: #E8E8E8 !important;
        border: 1px solid #002D5E !important;
        border-radius: 4px !important;
    }
    
    /* Botões Profissionais */
    .stButton>button {
        background-color: #E8E8E8 !important;
        color: #002D5E !important;
        border: 2px solid #002D5E !important;
        border-radius: 6px !important;
        font-weight: bold; width: 100%;
        transition: 0.3s;
    }
    .stButton>button:hover { background-color: #002D5E !important; color: #FFFFFF !important; }
    
    /* Logo com Sombra */
    .logo-aura { filter: drop-shadow(0px 4px 8px rgba(0,0,0,0.5)); display: block; margin: auto; }
    </style>
    """, unsafe_allow_html=True)

# 2. LÓGICA DE BANCO DE DADOS (GITHUB)
def conectar_github():
    try:
        token = st.secrets["GITHUB_TOKEN"]
        g = Github(token)
        repo = g.get_user().get_repo("logistica-aura") # Certifique-se que o nome do repo está correto
        return repo
    except:
        return None

def gerenciar_dados(repo, acao="carregar", df_novo=None, sha=None):
    file_path = "dados_logistica.csv"
    if acao == "carregar":
        try:
            file_content = repo.get_contents(file_path)
            df = pd.read_csv(io.StringIO(file_content.decoded_content.decode('utf-8')))
            return df, file_content.sha
        except:
            return pd.DataFrame(columns=["Data", "Motorista", "Passageiro", "Trajeto", "Valor"]), None
    else:
        csv_string = df_novo.to_csv(index=False)
        if sha:
            repo.update_file(file_path, "Update Logística", csv_string, sha)
        else:
            repo.create_file(file_path, "Iniciando Banco de Dados", csv_string)

# 3. CONTROLE DE ACESSO E PRIVACIDADE (O ESCUDO)
if 'aceite_lgpd' not in st.session_state:
    st.session_state.aceite_lgpd = False

if not st.session_state.aceite_lgpd:
    st.subheader("🛡️ Termos de Uso e Privacidade")
    st.info("Para acessar a Ferramenta de Logística da Aura Apoena, você deve concordar com o tratamento de dados.")
    
    with st.expander("Ver Política de Privacidade completa (LGPD)"):
        st.write("""
            **Finalidade:** Os dados coletados (Nomes e Trajetos) são para fins exclusivos de gestão logística.
            **Segurança:** Seus dados são armazenados de forma criptografada no repositório da empresa.
            **Responsabilidade:** O usuário se compromete a inserir dados verídicos.
        """)
    
    check_consentimento = st.checkbox("Li e aceito os termos de tratamento de dados conforme a LGPD.")
    if st.button("Acessar Plataforma"):
        if check_consentimento:
            st.session_state.aceite_lgpd = True
            st.rerun()
        else:
            st.warning("É necessário aceitar os termos para prosseguir.")
    st.stop()

# 4. INTERFACE PRINCIPAL (NAVBAR LATERAL)
repo = conectar_github()
if repo:
    df, sha = gerenciar_dados(repo, "carregar")

    with st.sidebar:
        st.markdown('<div style="text-align: center;"><img src="https://gist.githubusercontent.com/user-attachments/assets/8e0f5228-40b9-4674-9f0f-6df3d57b280c" width="180" class="logo-aura"></div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        menu = st.radio("NAVEGAÇÃO", ["🏠 Home", "📝 Programar", "📋 Agenda", "💰 Financeiro", "⚙️ Suporte"])

    # TELA: HOME (DASHBOARD)
    if menu == "🏠 Home":
        st.title("Bem-vinda, Yara!")
        st.write("Resumo das atividades da Logística Apoena.")
        c1, c2 = st.columns(2)
        c1.metric("Viagens Programadas", len(df))
        c2.metric("Custo Total (R$)", f"{df['Valor'].sum():.2f}")

    # TELA: PROGRAMAR (MASCARAMENTO E FEEDBACK)
    elif menu == "📝 Programar":
        st.header("📝 Nova Programação")
        with st.form("form_viagem", clear_on_submit=True):
            col1, col2 = st.columns(2)
            # Mascaramento é feito via interface: forçando maiúsculas
            pax = col1.text_input("Passageiro").upper()
            mot = col1.selectbox("Motorista", ["Ilson", "Antonio", "Terceirizado"])
            data = col2.date_input("Data da Viagem", datetime.now())
            tra = col2.selectbox("Trajeto", ["P. Lacerda x Cuiabá", "Cuiabá x P. Lacerda", "Interno", "Outro"])
            
            if st.form_submit_button("✅ SALVAR REGISTRO"):
                if pax == "":
                    st.error("O campo Passageiro não pode ficar vazio.")
                else:
                    with st.spinner("Sincronizando com a nuvem..."):
                        nova_linha = pd.DataFrame([{"Data": data.strftime('%d/%m/%Y'), "Motorista": mot, "Passageiro": pax, "Trajeto": tra, "Valor": 0}])
                        df_final = pd.concat([df, nova_linha], ignore_index=True)
                        gerenciar_dados(repo, "salvar", df_final, sha)
                        st.success("Viagem cadastrada com sucesso!")

    # TELA: FINANCEIRO (SEGURANÇA DE EXCLUSÃO)
    elif menu == "💰 Financeiro":
        st.header("💰 Controle de Custos")
        st.write("Edite os valores ou adicione informações financeiras abaixo.")
        df_editado = st.data_editor(df, use_container_width=True, num_rows="dynamic")
        
        # Confirmação de exclusão ou alteração importante
        if st.button("💾 SALVAR ALTERAÇÕES"):
            st.warning("⚠️ Você está prestes a sobrescrever os dados no GitHub.")
            confirmar = st.checkbox("Confirmo que revisei os valores e desejo salvar.")
            if confirmar:
                with st.spinner("Atualizando banco de dados..."):
                    gerenciar_dados(repo, "salvar", df_editado, sha)
                    st.success("Dados atualizados!")
                    st.rerun()

    # TELA: SUPORTE
    elif menu == "⚙️ Suporte":
        st.header("⚙️ Central de Ajuda")
        st.write("Dúvidas ou bugs? Entre em contato com o suporte de infraestrutura.")
        st.button("Reportar um Problema")
