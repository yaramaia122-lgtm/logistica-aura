import streamlit as st
import pandas as pd
from github import Github
import io
from datetime import datetime

# 1. PREVENÇÃO CONTRA TRADUTOR E IDIOMA
st.markdown('<html lang="pt-br">', unsafe_allow_html=True)

# 2. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Logística Aura Apoena", layout="wide")

# 3. UI/UX DESIGNER (ENGENHARIA DE INTERFACE)
st.markdown("""
    <style>
    /* Fundo Principal - Cinza quase branco para não cansar a vista */
    .stApp { background-color: #FDFDFD; }
    
    /* Barra Lateral - Azul Marinho Aura */
    [data-testid="stSidebar"] {
        background-color: #002D5E !important;
        min-width: 300px;
    }
    
    /* Ajuste de cor dos textos na Barra Lateral */
    [data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] p, [data-testid="stSidebar"] label {
        color: #FFFFFF !important;
        font-weight: 500;
    }

    /* Estilização das Caixas de Texto (Contraste Máximo) */
    .stTextInput input, .stSelectbox div[data-baseweb="select"], .stDateInput input {
        background-color: #FFFFFF !important;
        border: 2px solid #E0E0E0 !important;
        color: #1A1A1A !important; /* Texto Escuro para leitura fácil */
        border-radius: 6px !important;
        height: 45px !important;
    }
    
    /* Títulos e Cabeçalhos */
    h1, h2, h3 { 
        color: #002D5E !important; 
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    /* Botão Salvar - Estilo Profissional */
    div.stButton > button {
        background-color: #002D5E;
        color: #FFFFFF;
        border: none;
        border-radius: 6px;
        padding: 0.7rem 1.5rem;
        font-size: 16px;
        font-weight: bold;
        width: 100%;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        transition: background 0.3s;
    }
    
    div.stButton > button:hover {
        background-color: #00428A !important;
        color: white !important;
    }

    /* Tabela de Dados */
    [data-testid="stDataFrame"] {
        border: 1px solid #E0E0E0;
        border-radius: 8px;
    }
    </style>
    """, unsafe_allow_html=True)

# 4. BACKEND (CONEXÃO GITHUB)
def carregar_sistema():
    try:
        g = Github(st.secrets["GITHUB_TOKEN"])
        repo = g.get_repo("yaramaia122-lgtm/logistica-aura")
        contents = repo.get_contents("dados_logistica.csv")
        df = pd.read_csv(io.StringIO(contents.decoded_content.decode()))
        return df, contents.sha, repo
    except:
        # Se falhar ou arquivo não existir, inicia vazio com colunas
        return pd.DataFrame(columns=["Passageiro", "Motorista", "Data", "Trajeto"]), None, None

df, sha, repo = carregar_sistema()

# 5. SIDEBAR / MENU
with st.sidebar:
    # CORREÇÃO DA LOGO: Usando o caminho direto do repositório no GitHub
    # Adicionamos um espaçador para a logo não ficar colada no topo
    st.markdown("<br>", unsafe_allow_html=True)
    
    logo_path = "https://raw.githubusercontent.com/yaramaia122-lgtm/logistica-aura/main/Aura%20(Azul%20e%20Ocre)%20(1).png"
    
    # O comando st.image precisa da URL correta e sem o parâmetro "0" que causava o erro
    st.image(logo_path, width=250)
    
    st.markdown("---")
    menu = st.radio("Navegação", ["📋 Agenda de Viagens", "📝 Programar Nova Viagem", "💰 Financeiro e Edição"])

# 6. TELAS
if menu == "📝 Programar Nova Viagem":
    st.title("📝 Programar Nova Viagem")
    with st.form("form_logistica"):
        c1, c2 = st.columns(2)
        with c1:
            nome = st.text_input("Passageiro (Nome Completo)").upper()
            motorista = st.selectbox("Motorista", ["Ilson", "Antonio", "Outro"])
        with c2:
            data = st.date_input("Data da Viagem", datetime.now())
            trajeto = st.selectbox("Trajeto", ["P. Lacerda x Cuiabá", "Interno", "Outro"])
        
        # Botão de ação
        if st.form_submit_button("Confirmar Agendamento"):
            if nome and repo:
                nova_viagem = pd.DataFrame([[nome, motorista, data.strftime('%d/%m/%Y'), trajeto]], columns=df.columns)
                df_atualizado = pd.concat([df, nova_viagem], ignore_index=True)
                csv_txt = df_atualizado.to_csv(index=False)
                
                if sha:
                    repo.update_file("dados_logistica.csv", "Registro de Viagem", csv_txt, sha)
                else:
                    repo.create_file("dados_logistica.csv", "Início do Banco", csv_txt)
                
                st.success(f"Viagem para {nome} salva com sucesso!")
                st.rerun()
            else:
                st.error("Preencha o nome do passageiro antes de salvar.")

elif menu == "📋 Agenda de Viagens":
    st.title("📋 Agenda de Logística")
    if df.empty:
        st.info("Não há viagens registradas no momento.")
    else:
        # Mostra a tabela ocupando a largura total
        st.dataframe(df, width="stretch")

elif menu == "💰 Financeiro e Edição":
    st.title("💰 Gestão de Registros")
    st.markdown("Edite os dados diretamente na tabela abaixo e clique em salvar:")
    
    # Editor de dados (substituindo o parâmetro antigo pelo novo sugerido pelo log)
    df_editado = st.data_editor(df, num_rows="dynamic", width="stretch")
    
    if st.button("Salvar Todas as Alterações"):
        if repo:
            csv_editado = df_editado.to_csv(index=False)
            repo.update_file("dados_logistica.csv", "Edição Manual", csv_editado, sha)
            st.success("Dados atualizados no GitHub!")
            st.rerun()
