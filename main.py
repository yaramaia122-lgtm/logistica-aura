import streamlit as st
import pandas as pd
from github import Github, Auth
import io
import os
from datetime import datetime

# ==========================================================
# 0. INICIALIZAÇÃO DE SESSÃO (LOGIN)
# ==========================================================
if 'logado' not in st.session_state:
    st.session_state['logado'] = False
    st.session_state['usuario_atual'] = ""

# ==========================================================
# 1. FORÇAR TEMA CLARO E CONFIGURAÇÃO DA PÁGINA
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

st.set_page_config(page_title="Aura Apoena Logistics", layout="wide")
forcar_tema_claro()

# ==========================================================
# 2. TELA DE LOGIN (TUDO AZUL MARINHO)
# ==========================================================
if not st.session_state['logado']:
    
    # --- CSS EXCLUSIVO PARA O LOGIN ---
    st.markdown("""
    <style>
        /* Fundo de toda a tela em Azul Marinho */
        .stApp { background-color: #002D5E !important; }
        
        /* Esconde o botão de abrir menu lateral no login */
        [data-testid="collapsedControl"] { display: none !important; }
        
        /* Letras e Títulos em Branco para dar contraste */
        h1, h2, h3, label, p { color: #FFFFFF !important; font-weight: bold !important; }
        
        /* Campos de digitar Usuário e Senha */
        .stTextInput input { 
            background-color: #F0F7FF !important; 
            color: #002D5E !important; 
            border: none !important; 
            border-radius: 8px !important; 
            font-weight: bold !important;
        }
        input { -webkit-text-fill-color: #002D5E !important; }
        
        /* === BOTÃO DE ENTRAR CORRIGIDO (BLINDAGEM TOTAL) === */
        div.stButton > button { 
            background-color: #FFFFFF !important; 
            border: 2px solid #FFFFFF !important; 
            border-radius: 8px !important;
            width: 100% !important; 
            height: 55px !important; 
        }
        
        /* Força a letra Azul Marinho no estado normal para NÃO sumir */
        div.stButton > button, 
        div.stButton > button p, 
        div.stButton > button span, 
        div.stButton > button div {
            color: #002D5E !important; 
            font-size: 18px !important;
            font-weight: 900 !important; 
        }
        
        /* Efeito de passar o mouse (Hover) */
        div.stButton > button:hover {
            background-color: #002D5E !important;
            border-color: #FFFFFF !important;
        }
        div.stButton > button:hover, 
        div.stButton > button:hover p, 
        div.stButton > button:hover span, 
        div.stButton > button:hover div {
            color: #FFFFFF !important;
        }
    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        # Logo reduzida e centralizada
        st.image("https://raw.githubusercontent.com/yaramaia122-lgtm/logistica-aura/main/logo.png", width=220)
        st.markdown("<h2 style='color: white;'>🔐 Portal Logístico</h2>", unsafe_allow_html=True)
        
        with st.form("form_login"):
            usuario_digitado = st.text_input("Usuário Corporativo")
            senha_digitada = st.text_input("Senha de Acesso", type="password")
            st.markdown("<br>", unsafe_allow_html=True)
            entrar = st.form_submit_button("ENTRAR NO SISTEMA")
            
            if entrar:
                # === LISTA DE USUÁRIOS E SENHAS ===
                usuarios_permitidos = {
                    "admin": "aura123",
                    "yara": "1234",
                    "motorista": "log2026"
                }
                
                usuario_limpo = usuario_digitado.strip().lower()
                
                if usuario_limpo in usuarios_permitidos and usuarios_permitidos[usuario_limpo] == senha_digitada:
                    st.session_state['logado'] = True
                    st.session_state['usuario_atual'] = usuario_limpo
                    st.rerun()
                else:
                    st.error("❌ Usuário ou senha incorretos. Acesso negado.")

# ==========================================================
# 3. APP PRINCIPAL (SÓ CARREGA DEPOIS DO LOGIN)
# ==========================================================
else:
    # --- CSS EXCLUSIVO DO APP (FUNDO BRANCO, BARRA AZUL) ---
    st.markdown("""
    <style>
        .stApp { background-color: #FFFFFF !important; }
        [data-testid="stSidebar"] { background-color: #002D5E !important; }
        [data-testid="stSidebar"] [data-testid="stImage"] img { filter: drop-shadow(0px 10px 15px rgba(0,0,0,0.6)); }
        
        /* Textos do meio da tela em Azul Marinho */
        h1, h2, h3, label, .stMarkdown p { color: #002D5E !important; font-weight: 700 !important; opacity: 1 !important; }
        
        /* Textos da Barra Lateral em Branco */
        [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, 
        [data-testid="stSidebar"] p, [data-testid="stSidebar"] label, [data-testid="stSidebar"] span { color: #FFFFFF !important; }

        /* Campos de Preenchimento */
        .stTextInput input, .stSelectbox div[data-baseweb="select"], .stDateInput input, .stNumberInput input { 
            background-color: #F0F7FF !important; border: 2px solid #002D5E !important; border-radius: 6px !important; 
        }
        input { color: #002D5E !important; -webkit-text-fill-color: #002D5E !important; font-weight: 600 !important; }
        div[data-baseweb="select"] span { color: #002D5E !important; font-weight: 600 !important; }
        
        /* Botões do App */
        div.stButton > button { background-color: #E1E8F0 !important; color: #002D5E !important; border: 2px solid #002D5E !important; font-weight: 800 !important; width: 100% !important; height: 50px !important; }
        div.stButton > button p { color: #002D5E !important; }
        
        /* Tabelas */
        table { width: 100%; border-collapse: collapse; }
        th { background-color: #E1E8F0 !important; color: #002D5E !important; font-weight: 900 !important; font-size: 16px !important; border-bottom: 3px solid #002D5E !important; padding: 12px !important; text-align: left !important; }
        td { background-color: #F0F7FF !important; color: #000000 !important; border-bottom: 1px solid #B0C4DE !important; padding: 10px !important; font-size: 15px !important; }
    </style>
    """, unsafe_allow_html=True)

    # --- Backend Github ---
    def carregar_dados():
        cols = ["Passageiro", "Motorista", "Data", "Trajeto", "Centro de Custo", "Obs", "Hotel", "Combustivel", "Aereo", "Outros", "Total", "Aceite_LGPD", "Usuario_Criador"]
        try:
            token = st.secrets["GITHUB_TOKEN"]
            auth = Auth.Token(token)
            g = Github(auth=auth)
            
            repo = g.get_repo("yaramaia122-lgtm/logistica-aura")
            contents = repo.get_contents("dados_logistica.csv")
            df = pd.read_csv(io.StringIO(contents.decoded_content.decode()))
            for c in cols:
                if c not in df.columns: df[c] = 0.0 if c in ["Hotel", "Combustivel", "Aereo", "Outros", "Total"] else ""
            return df, contents.sha, repo, g
        except:
            return pd.DataFrame(columns=cols), None, None, None

    df, sha, repo, g = carregar_dados()

    # --- Sidebar / Menu ---
    with st.sidebar:
        st.markdown("<br>", unsafe_allow_html=True)
        st.image("https://raw.githubusercontent.com/yaramaia122-lgtm/logistica-aura/main/logo.png", width=220)
        st.markdown(f"<p style='color: white; text-align: center;'>Logado como: <b>{st.session_state['usuario_atual'].upper()}</b></p>", unsafe_allow_html=True)
        st.markdown("---")
        
        menu = st.radio("NAVEGAÇÃO", ["Agenda", "Programar Viagem", "Financeiro (Acesso ADM)"])
        
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        
        if st.button("Sair / Logout"):
            st.session_state['logado'] = False
            st.session_state['usuario_atual'] = ""
            st.rerun()
            
        st.markdown("---")
        with st.expander("🛡️ Política de Privacidade LGPD"):
            st.caption("""
            **Uso Interno:** Este app gerencia o fluxo de viagens da Aura. 
            Os dados (nomes e custos) são sigilosos e armazenados em nuvem criptografada.
            O acesso financeiro exige trava de segurança. Ao cadastrar, você concorda com os termos corporativos.
            """)

    # --- Telas ---
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
        
        if not df.empty and "Centro de Custo" in df.columns:
            usados_no_banco = df["Centro de Custo"].dropna().unique().tolist()
            lista_completa = sorted(list(set(lista_base + usados_no_banco)))
        else:
            lista_completa = sorted(lista_base)
            
        cc_selecionado = col1.selectbox("Centro de Custo (Selecione na lista)", lista_completa)
        novo_cc = col1.text_input("➕ Não achou? Cadastre um Novo Centro de Custo aqui:")
        
        v_h = col1.number_input("Custo Hotel (R$)", min_value=0.0)
        v_a = col1.number_input("Custo Aéreo (R$)", min_value=0.0)
        
        data = col2.date_input("Data da Viagem", datetime.now(), format="DD/MM/YYYY")
        traj = col2.selectbox("Itinerário Principal", ["P. Lacerda x Cuiabá", "Interno", "Outro"])
        v_c = col2.number_input("Custo Combustível (R$)", min_value=0.0)
        v_o = col2.number_input("Outros Custos (R$)", min_value=0.0)
        
        obs = form.text_input("Observações Adicionais")
        
        st.markdown("---")
        aceite_lgpd = form.checkbox("Li e concordo com a Política de Privacidade (LGPD)")
        
        gravar = form.form_submit_button("GRAVAR REGISTRO NO SISTEMA")

        if gravar:
            centro_custo_final = novo_cc.strip() if novo_cc.strip() != "" else cc_selecionado

            if not nome:
                st.warning("⚠️ ERRO: O campo 'Nome do Passageiro' não pode ficar vazio.")
            elif not aceite_lgpd:
                st.warning("⚠️ ERRO: Você deve concordar com a Política de Privacidade para gravar.")
            elif not repo:
                st.error("❌ ERRO DE CONEXÃO: Não foi possível conectar ao banco de dados (Verifique o Token).")
            else:
                total = v_h + v_c + v_a + v_o
                timestamp_aceite = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                usuario_criador = st.session_state['usuario_atual']
                
                nova_viagem = pd.DataFrame([[nome, moto, data.strftime('%d/%m/%Y'), traj, centro_custo_final, obs, v_h, v_c, v_a, v_o, total, timestamp_aceite, usuario_criador]], columns=df.columns)
                df_final = pd.concat([df, nova_viagem], ignore_index=True)
                
                repo.update_file("dados_logistica.csv", "Registro de Viagem", df_final.to_csv(index=False), sha)
                st.success("✅ VIAGEM PROGRAMADA COM SUCESSO!")
                st.rerun()

    elif menu == "Financeiro (Acesso ADM)":
        st.title("💰 Controle Financeiro (Restrito)")
        
        senha = st.text_input("Digite a senha de Administrador de Finanças:", type="password")
        
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
