import streamlit as st
import pandas as pd
from github import Github
import io
import os
from datetime import datetime

# ==========================================================
# 1. FORÇAR TEMA CLARO
# ==========================================================
def forcar_tema_claro():
    try:
        os.makedirs(".streamlit", exist_ok=True)
        arquivo = ".streamlit/config.toml"
        conteudo = "[theme]\nbase='light'\nprimaryColor='#002D5E'\n"
        precisa_escrever = True
        if os.path.exists(arquivo):
            with open(arquivo, "r") as f:
                if conteudo in f.read(): precisa_escrever = False
        if precisa_escrever:
            with open(arquivo, "w") as f: f.write(conteudo)
    except:
        pass

forcar_tema_claro()

# ==========================================================
# 2. CONFIGURAÇÃO DA PÁGINA
# ==========================================================
st.set_page_config(page_title="Aura Apoena Logistics", layout="wide")

# ==========================================================
# 3. UI/UX - ESTILO DEFINITIVO (INTOCADO)
# ==========================================================
st.markdown("""
<style>
    .stApp { background-color: #FFFFFF !important; }
    [data-testid="stSidebar"] { background-color: #002D5E !important; }
    [data-testid="stSidebar"] [data-testid="stImage"] img { filter: drop-shadow(0px 10px 15px rgba(0,0,0,0.6)); }
    h1, h2, h3, label, .stMarkdown p { color: #002D5E !important; font-weight: 700 !important; opacity: 1 !important; }
    
    /* BARRA LATERAL BRANCA */
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, 
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] label, [data-testid="stSidebar"] span { color: #FFFFFF !important; }

    /* Campos de Preenchimento */
    .stTextInput input, .stSelectbox div[data-baseweb="select"], .stDateInput input, .stNumberInput input { 
        background-color: #F0F7FF !important; border: 2px solid #002D5E !important; border-radius: 6px !important; 
    }
    input { color: #002D5E !important; -webkit-text-fill-color: #002D5E !important; font-weight: 600 !important; }
    div[data-baseweb="select"] span { color: #002D5E !important; font-weight: 600 !important; }
    
    /* Botões */
    div.stButton > button { background-color: #E1E8F0 !important; color: #002D5E !important; border: 2px solid #002D5E !important; font-weight: 800 !important; width: 100% !important; height: 50px !important; }
    
    /* Tabela */
    table { width: 100%; border-collapse: collapse; }
    th { background-color: #E1E8F0 !important; color: #002D5E !important; font-weight: 900 !important; font-size: 16px !important; border-bottom: 3px solid #002D5E !important; padding: 12px !important; text-align: left !important; }
    td { background-color: #F0F7FF !important; color: #000000 !important; border-bottom: 1px solid #B0C4DE !important; padding: 10px !important; font-size: 15px !important; }
</style>
""", unsafe_allow_html=True)

# ==========================================================
# 4. BACKEND GITHUB 
# ==========================================================
def carregar_dados():
    cols = ["Passageiro", "Motorista", "Data", "Trajeto", "Centro de Custo", "Obs", "Hotel", "Combustivel", "Aereo", "Outros", "Total"]
    try:
        g = Github(st.secrets["GITHUB_TOKEN"])
        repo = g.get_repo("yaramaia122-lgtm/logistica-aura")
        contents = repo.get_contents("dados_logistica.csv")
        df = pd.read_csv(io.StringIO(contents.decoded_content.decode()))
        for c in cols:
            if c not in df.columns: df[c] = 0.0 if c in ["Hotel", "Combustivel", "Aereo", "Outros", "Total"] else ""
        return df, contents.sha, repo
    except:
        return pd.DataFrame(columns=cols), None, None

df, sha, repo = carregar_dados()

# ==========================================================
# 5. SIDEBAR / MENU
# ==========================================================
with st.sidebar:
    st.markdown("<br>", unsafe_allow_html=True)
    st.image("https://raw.githubusercontent.com/yaramaia122-lgtm/logistica-aura/main/logo.png", width=220)
    st.markdown("---")
    menu = st.radio("NAVEGAÇÃO", ["Agenda", "Programar Viagem", "Financeiro (Acesso ADM)"])

# ==========================================================
# 6. TELAS E APLICAÇÃO
# ==========================================================
if menu == "Agenda":
    st.title("📋 Agenda de Viagens")
    if not df.empty:
        st.table(df[["Passageiro", "Motorista", "Data", "Trajeto", "Centro de Custo", "Obs"]])
    else:
        st.info("Nenhuma viagem agendada.")

elif menu == "Programar Viagem":
    st.title("📝 Programar Viagem")
    
    form = st.form("meu_form", clear_on_submit=True)
    col1, col2 = form.columns(2)
    
    nome = col1.text_input("Nome do Passageiro").upper()
    moto = col1.selectbox("Motorista Designado", ["Ilson", "Antonio", "Outro"])
    
    # === SISTEMA INTELIGENTE DE CENTRO DE CUSTO (CORRIGIDO) ===
    lista_base = [
        "210301 - Moagem", "210403 - Detox", "210801 - Laboratório", "211002 - Manutenção Mecânica Planta",
        "210405 - Lixiviação / Cianetação", "210101 - Administração Planta", "211001 - Manutencao Eletrica Planta",
        "211003 - Oficina Manutenção Planta", "210201 - Britagem Primária", "210604 - Fundição",
        "310101 - Almoxarifado", "320401 - Controladoria e Contabilidade", "310701 - Serviços Gerais",
        "320601 - Celula de Gestao de Contratos", "320101 - Suprimentos", "320502 - Tecnologia da Informação",
        "311202 - Care and Maintenance SF", "330102 - Apoena Corporativo", "311203 - Care and Maintenance PPQ",
        "340103 - Jurídico", "310801 - Seguranca Patrimonial", "310301 - PCP", "320201 - Gerência Geral",
        "310508 - Comunidades", "320303 - Trainee", "320301 - Recursos Humanos", "310902 - Campo",
        "310904 - Exploração EPP", "121101 - Geologia Operacional - Mina Ernesto",
        "121102 - Planejamento e Topografia Operacional - Mina Ernesto", "151101 - Geologia Operacional - Mina Nosde",
        "151103 - Geotecnia - Nosde", "210502 - Barragem", "151102 - Planejamento e Topografia Operacional - Mina Nosde",
        "310501 - Meio Ambiente", "310503 - Segurança do Trabalho", "310502 - Saude",
        "150101 - Administração de Mina - Céu Aberto - Nosde", "120101 - Administração de Mina - Céu Aberto - Ernesto"
    ]
    
    # Pega os centros de custo que já estão no banco de dados
    if not df.empty and "Centro de Custo" in df.columns:
        usados_no_banco = df["Centro de Custo"].dropna().unique().tolist()
        lista_completa = sorted(list(set(lista_base + usados_no_banco)))
    else:
        lista_completa = sorted(lista_base)
        
    # Campo 1: A lista padrão
    cc_selecionado = col1.selectbox("Centro de Custo (Selecione na lista)", lista_completa)
    
    # Campo 2: A caixinha opcional sempre visível (resolve o bug do botão)
    novo_cc = col1.text_input("➕ Não achou? Cadastre um Novo Centro de Custo aqui:")
    
    v_h = col1.number_input("Custo Hotel (R$)", min_value=0.0)
    v_a = col1.number_input("Custo Aéreo (R$)", min_value=0.0)
    
    data = col2.date_input("Data da Viagem", datetime.now())
    traj = col2.selectbox("Itinerário Principal", ["P. Lacerda x Cuiabá", "Interno", "Outro"])
    v_c = col2.number_input("Custo Combustível (R$)", min_value=0.0)
    v_o = col2.number_input("Outros Custos (R$)", min_value=0.0)
    
    obs = form.text_input("Observações Adicionais")
    gravar = form.form_submit_button("GRAVAR REGISTRO NO SISTEMA")

    if gravar:
        # A Mágica acontece aqui: se digitou algo na caixinha, usa ela. Senão, usa a lista.
        centro_custo_final = novo_cc.strip() if novo_cc.strip() != "" else cc_selecionado

        if not nome:
            st.warning("⚠️ ERRO: O campo 'Nome do Passageiro' não pode ficar vazio.")
        elif not repo:
            st.error("❌ ERRO DE CONEXÃO: Não foi possível conectar ao banco de dados (Verifique o Token).")
        else:
            total = v_h + v_c + v_a + v_o
            nova_viagem = pd.DataFrame([[nome, moto, data.strftime('%d/%m/%Y'), traj, centro_custo_final, obs, v_h, v_c, v_a, v_o, total]], columns=df.columns)
            df_final = pd.concat([df, nova_viagem], ignore_index=True)
            
            repo.update_file("dados_logistica.csv", "Registro de Viagem", df_final.to_csv(index=False), sha)
            st.success("✅ VIAGEM PROGRAMADA COM SUCESSO!")
            st.rerun()

elif menu == "Financeiro (Acesso ADM)":
    st.title("💰 Controle Financeiro (Restrito)")
    
    # === A SENHA FICA AQUI ===
    senha = st.text_input("Digite a senha de Administrador:", type="password")
    
    if senha == "aura123":
        st.success("Acesso Liberado.")
        df_ed = st.data_editor(df, num_rows="dynamic", use_container_width=True)
        
        if st.button("SALVAR ALTERAÇÕES FINANCEIRAS"):
            if repo:
                df_ed["Total"] = df_ed["Hotel"] + df_ed["Combustivel"] + df_ed["Aereo"] + df_ed["Outros"]
                repo.update_file("dados_logistica.csv", "Edição Financeira", df_ed.to_csv(index=False), sha)
                st.success("✅ ALTERAÇÕES REGISTRADAS NO BANCO DE DADOS!")
                st.rerun()
    elif senha != "":
        st.error("Senha incorreta. Acesso negado.")
