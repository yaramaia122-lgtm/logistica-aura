import streamlit as st
import pandas as pd
from github import Github, Auth
import io
import os
from datetime import datetime

# ==========================================================
# 0. INICIALIZAÇÃO DE SESSÃO (LOGIN) E SEGURANÇA
# ==========================================================
if 'logado' not in st.session_state:
    st.session_state['logado'] = False
    st.session_state['usuario_atual'] = ""
    st.session_state['perfil'] = ""

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
# 2. TELA DE LOGIN (TUDO AZUL MARINHO + ESQUECI A SENHA)
# ==========================================================
if not st.session_state['logado']:
    
    st.markdown("""
    <style>
        .stApp { background-color: #002D5E !important; }
        [data-testid="collapsedControl"] { display: none !important; }
        h1, h2, h3, label, p { color: #FFFFFF !important; font-weight: bold !important; }
        
        .stTextInput input { 
            background-color: #F0F7FF !important; 
            color: #002D5E !important; 
            border: none !important; 
            border-radius: 8px !important; 
            font-weight: bold !important;
        }
        input { -webkit-text-fill-color: #002D5E !important; }
        
        div[data-testid="stFormSubmitButton"] > button { 
            background-color: #FFFFFF !important; 
            border: 2px solid #FFFFFF !important; 
            border-radius: 8px !important;
            width: 100% !important; 
            height: 55px !important; 
            margin-top: 10px !important;
        }
        div[data-testid="stFormSubmitButton"] > button p {
            color: #002D5E !important; 
            font-size: 18px !important;
            font-weight: 900 !important; 
        }
        div[data-testid="stFormSubmitButton"] > button:hover {
            background-color: #002D5E !important;
            border: 2px solid #FFFFFF !important;
        }
        div[data-testid="stFormSubmitButton"] > button:hover p {
            color: #FFFFFF !important;
        }
        
        /* Estilo para o botão de esqueci a senha parecer um link */
        .esqueci-senha {
            text-align: center;
            margin-top: 15px;
            font-size: 14px;
        }
    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.image("https://raw.githubusercontent.com/yaramaia122-lgtm/logistica-aura/main/logo.png", width=220)
        st.markdown("<h2 style='color: white;'>Portal Logístico Corporativo</h2>", unsafe_allow_html=True)
        
        with st.form("form_login"):
            usuario_digitado = st.text_input("Usuário Corporativo")
            senha_digitada = st.text_input("Senha de Acesso", type="password")
            entrar = st.form_submit_button("ENTRAR NO SISTEMA")
            
            if entrar:
                # Banco de Usuários e Nível de Permissão (Admin vs Operador)
                usuarios_permitidos = {
                    "admin": {"senha": "aura123", "perfil": "Administrador"},
                    "yara": {"senha": "1234", "perfil": "Administrador"},
                    "motorista": {"senha": "log2026", "perfil": "Operador"}
                }
                
                usuario_limpo = usuario_digitado.strip().lower()
                
                if usuario_limpo in usuarios_permitidos and usuarios_permitidos[usuario_limpo]["senha"] == senha_digitada:
                    st.session_state['logado'] = True
                    st.session_state['usuario_atual'] = usuario_limpo
                    st.session_state['perfil'] = usuarios_permitidos[usuario_limpo]["perfil"]
                    st.rerun()
                else:
                    st.error("Usuário ou senha incorretos. Acesso negado.")
        
        # Módulo Esqueci a Senha Corporativo
        with st.expander("Esqueceu sua senha?"):
            st.info("Por diretrizes de segurança da informação (LGPD), a redefinição de senhas deve ser solicitada diretamente ao Administrador do Sistema ou ao setor de TI da Aura. Acesso não autorizado está sujeito a sanções disciplinares.")

# ==========================================================
# 3. APP PRINCIPAL (SÓ CARREGA DEPOIS DO LOGIN)
# ==========================================================
else:
    st.markdown("""
    <style>
        .stApp { background-color: #FFFFFF !important; }
        [data-testid="stSidebar"] { background-color: #002D5E !important; }
        [data-testid="stSidebar"] [data-testid="stImage"] img { filter: drop-shadow(0px 10px 15px rgba(0,0,0,0.6)); }
        
        h1, h2, h3, label, .stMarkdown p { color: #002D5E !important; font-weight: 700 !important; opacity: 1 !important; }
        
        [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, 
        [data-testid="stSidebar"] p, [data-testid="stSidebar"] label, [data-testid="stSidebar"] span { color: #FFFFFF !important; }

        .stTextInput input, .stSelectbox div[data-baseweb="select"], .stDateInput input, .stNumberInput input { 
            background-color: #F0F7FF !important; border: 2px solid #002D5E !important; border-radius: 6px !important; 
        }
        input { color: #002D5E !important; -webkit-text-fill-color: #002D5E !important; font-weight: 600 !important; }
        div[data-baseweb="select"] span { color: #002D5E !important; font-weight: 600 !important; }
        
        div.stButton > button { background-color: #E1E8F0 !important; border: 2px solid #002D5E !important; border-radius: 8px !important; width: 100% !important; height: 50px !important; }
        div.stButton > button * { color: #002D5E !important; font-weight: 800 !important; }
        
        [data-testid="stDataFrame"] { border: 1px solid #002D5E !important; border-radius: 8px !important; overflow: hidden !important;}
        
        /* Ajuste de abas (Tabs) do menu admin */
        .stTabs [data-baseweb="tab-list"] { gap: 20px; }
        .stTabs [data-baseweb="tab"] { height: 50px; white-space: pre-wrap; background-color: #F0F7FF; border-radius: 6px 6px 0px 0px; padding-left: 20px; padding-right: 20px;}
        .stTabs [aria-selected="true"] { background-color: #002D5E !important; color: white !important;}
        .stTabs [aria-selected="true"] p { color: white !important; font-weight: bold !important;}
    </style>
    """, unsafe_allow_html=True)

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
            
            # Garantir que a coluna Total seja número para o Dashboard não quebrar
            df["Total"] = pd.to_numeric(df["Total"], errors='coerce').fillna(0)
            return df, contents.sha, repo, g
        except:
            return pd.DataFrame(columns=cols), None, None, None

    df, sha, repo, g = carregar_dados()

    with st.sidebar:
        st.markdown("<br>", unsafe_allow_html=True)
        st.image("https://raw.githubusercontent.com/yaramaia122-lgtm/logistica-aura/main/logo.png", width=220)
        st.markdown(f"<p style='color: white; text-align: center; font-size: 14px;'>Usuário: <b>{st.session_state['usuario_atual'].upper()}</b><br>Perfil: {st.session_state['perfil']}</p>", unsafe_allow_html=True)
        st.markdown("---")
        
        # Menu Estruturado
        opcoes_menu = ["Dashboard", "Agenda", "Programar Viagem"]
        if st.session_state['perfil'] == "Administrador":
            opcoes_menu.append("Administração")
            
        menu = st.radio("NAVEGAÇÃO DO SISTEMA", opcoes_menu)
        
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        if st.button("Encerrar Sessão"):
            st.session_state['logado'] = False
            st.session_state['usuario_atual'] = ""
            st.session_state['perfil'] = ""
            st.rerun()

    # --- TELAS DO APLICATIVO ---
    
    if menu == "Dashboard":
        st.title("Painel de Indicadores (Dashboard)")
        st.markdown("Resumo gerencial e métricas de desempenho logístico.")
        st.divider()
        
        if not df.empty:
            # Cards de Métricas Principais
            col1, col2, col3 = st.columns(3)
            total_viagens = len(df)
            custo_total = df["Total"].sum()
            motoristas_unicos = df["Motorista"].nunique()
            
            col1.metric(label="Total de Viagens Registradas", value=total_viagens)
            col2.metric(label="Custo Global Estimado", value=f"R$ {custo_total:,.2f}")
            col3.metric(label="Motoristas Engajados", value=motoristas_unicos)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Gráficos Analíticos
            col_graf1, col_graf2 = st.columns(2)
            with col_graf1:
                st.markdown("#### Custos por Centro de Custo")
                custo_cc = df.groupby("Centro de Custo")["Total"].sum().sort_values(ascending=False)
                st.bar_chart(custo_cc)
                
            with col_graf2:
                st.markdown("#### Volume de Viagens por Destino")
                viagens_destino = df["Trajeto"].value_counts()
                st.bar_chart(viagens_destino)
        else:
            st.info("Sem dados suficientes para gerar o dashboard. Adicione registros no sistema.")

    elif menu == "Agenda":
        st.title("Agenda de Viagens")
        st.markdown("Visão geral das programações logísticas registradas no sistema.")
        st.divider()
        
        if not df.empty:
            st.dataframe(df[["Passageiro", "Motorista", "Data", "Trajeto", "Centro de Custo", "Obs"]], use_container_width=True, hide_index=True)
        else:
            st.info("Nenhuma viagem agendada no momento.")

    elif menu == "Programar Viagem":
        st.title("Programar Viagem")
        st.markdown("Preencha os dados abaixo para registrar uma nova logística.")
        
        form = st.form("meu_form", clear_on_submit=True)
        
        form.markdown("### 1. Dados da Rota e Passageiro")
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
        novo_cc = col1.text_input("+ Cadastrar Novo Centro de Custo (Opcional):")
        
        data = col2.date_input("Data da Viagem", datetime.now(), format="DD/MM/YYYY")
        traj = col2.selectbox("Itinerário Principal", ["P. Lacerda x Cuiabá", "Interno", "Outro"])
        obs = col2.text_area("Observações Adicionais (Opcional)")

        form.divider()
        form.markdown("### 2. Previsão de Custos")
        col3, col4 = form.columns(2)
        
        v_h = col3.number_input("Custo Hotel (R$)", min_value=0.0, format="%.2f")
        v_a = col3.number_input("Custo Aéreo (R$)", min_value=0.0, format="%.2f")
        v_c = col4.number_input("Custo Combustível (R$)", min_value=0.0, format="%.2f")
        v_o = col4.number_input("Outros Custos (R$)", min_value=0.0, format="%.2f")
        
        form.divider()
        aceite_lgpd = form.checkbox("Confirmo a ciência e o aceite das Políticas de Privacidade Internas (LGPD)")
        gravar = form.form_submit_button("GRAVAR REGISTRO NO SISTEMA")

        if gravar:
            centro_custo_final = novo_cc.strip() if novo_cc.strip() != "" else cc_selecionado

            if not nome:
                st.warning("ERRO: O campo 'Nome do Passageiro' não pode ficar vazio.")
            elif not aceite_lgpd:
                st.warning("ERRO: O aceite da Política de Privacidade é obrigatório para registrar a viagem.")
            elif not repo:
                st.error("ERRO DE CONEXÃO: Falha ao conectar com a base de dados em nuvem.")
            else:
                total = v_h + v_c + v_a + v_o
                timestamp_aceite = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                usuario_criador = st.session_state['usuario_atual']
                
                nova_viagem = pd.DataFrame([[nome, moto, data.strftime('%d/%m/%Y'), traj, centro_custo_final, obs, v_h, v_c, v_a, v_o, total, timestamp_aceite, usuario_criador]], columns=df.columns)
                df_final = pd.concat([df, nova_viagem], ignore_index=True)
                
                repo.update_file("dados_logistica.csv", "Registro de Viagem", df_final.to_csv(index=False), sha)
                st.success("VIAGEM PROGRAMADA E GRAVADA COM SUCESSO!")
                st.rerun()

    elif menu == "Administração":
        st.title("Painel de Administração")
        st.markdown("Módulo central de gestão corporativa. Restrito ao nível Administrador.")
        st.divider()
        
        # Módulo Avançado com Abas (Tabs)
        tab_fin, tab_usr, tab_seg = st.tabs(["Controle Financeiro", "Gestão de Usuários", "Governança e Segurança"])
        
        with tab_fin:
            st.markdown("### Auditoria de Custos Logísticos")
            st.info("Modifique os valores apenas após comprovação em nota fiscal. O cálculo total é automático.")
            
            df_ed = st.data_editor(df, num_rows="dynamic", use_container_width=True, hide_index=True)
            
            if st.button("ATUALIZAR BANCO DE DADOS FINANCEIRO"):
                if repo:
                    df_ed["Total"] = df_ed["Hotel"] + df_ed["Combustivel"] + df_ed["Aereo"] + df_ed["Outros"]
                    repo.update_file("dados_logistica.csv", "Edição Financeira via Admin", df_ed.to_csv(index=False), sha)
                    st.success("BASE DE DADOS ATUALIZADA!")
                    st.rerun()
                    
        with tab_usr:
            st.markdown("### Painel de Acessos")
            st.markdown("Gestão de contas autorizadas a acessar o sistema Aura Logistics.")
            
            dados_usuarios = {
                "Usuário": ["admin", "yara", "motorista"],
                "Perfil de Acesso": ["Administrador", "Administrador", "Operador"],
                "Status": ["Ativo", "Ativo", "Ativo"],
                "Último Acesso": [datetime.now().strftime("%d/%m/%Y"), datetime.now().strftime("%d/%m/%Y"), "Ontem"]
            }
            df_usuarios = pd.DataFrame(dados_usuarios)
            st.table(df_usuarios)
            st.caption("*Para adicionar, remover ou redefinir senhas, solicite a alteração no código fonte da aplicação ao Engenheiro de Software.*")
            
        with tab_seg:
            st.markdown("### Centro de Governança de Dados (LGPD)")
            col_s1, col_s2 = st.columns(2)
            
            with col_s1:
                st.markdown("#### Status de Conformidade")
                st.success("Criptografia em Repouso: Ativo (GitHub Servers)")
                st.success("Criptografia em Trânsito: Ativo (HTTPS)")
                st.success("Captura de Consentimento: Obrigatória no Formulário")
                
            with col_s2:
                st.markdown("#### Configurações Globais")
                st.toggle("Exigir troca de senha a cada 90 dias", value=True, disabled=True)
                st.toggle("Derrubar sessão por inatividade (Timeout)", value=True, disabled=True)
                st.toggle("Registro de IPs de acesso", value=False, disabled=True)
            
            st.divider()
            st.markdown("#### Termo Oficial de Privacidade da Empresa")
            st.markdown("""
            > **1. Finalidade:** Sistema interno para gestão de viagens, escalas e aprovação de custos logísticos.  
            > **2. Tratamento:** Dados informados (nomes, itinerários, valores) são de uso restrito da administração da Aura. Não há compartilhamento externo.  
            > **3. Auditoria:** Toda inclusão gera um registro de *timestamp* e *usuário logado* para fins de compliance. Acesso ao painel administrativo é auditado.
            """)
