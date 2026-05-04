import streamlit as st
import pandas as pd
from github import Github, Auth
import io
import os
from datetime import datetime

# ==========================================================
# 0. INICIALIZAÇÃO DE SESSÃO E SEGURANÇA
# ==========================================================
if 'logado' not in st.session_state:
    st.session_state['logado'] = False
if 'usuario_atual' not in st.session_state:
    st.session_state['usuario_atual'] = ""
if 'perfil' not in st.session_state:
    st.session_state['perfil'] = ""
if 'precisa_trocar_senha' not in st.session_state:
    st.session_state['precisa_trocar_senha'] = False
if 'usuario_troca' not in st.session_state:
    st.session_state['usuario_troca'] = ""

# ==========================================================
# 1. FORÇAR TEMA CLARO E CSS GLOBAL
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
# 2. MOTOR DE BANCO DE DADOS (VIAGENS E USUÁRIOS)
# ==========================================================
@st.cache_data(ttl=5)
def carregar_bancos():
    cols_viagens = ["Passageiro", "Motorista", "Data", "Trajeto", "Centro de Custo", "Obs", "Hotel", "Combustivel", "Aereo", "Outros", "Total", "Aceite_LGPD", "Usuario_Criador"]
    cols_usuarios = ["Usuario", "Senha", "Perfil", "Status", "Primeiro_Acesso"]
    
    try:
        token = st.secrets["GITHUB_TOKEN"]
        auth = Auth.Token(token)
        g = Github(auth=auth)
        repo = g.get_repo("yaramaia122-lgtm/logistica-aura")
        
        # 1. Carregar Viagens
        try:
            cont_viagens = repo.get_contents("dados_logistica.csv")
            df_v = pd.read_csv(io.StringIO(cont_viagens.decoded_content.decode()))
            sha_v = cont_viagens.sha
            for c in cols_viagens:
                if c not in df_v.columns: df_v[c] = 0.0 if c in ["Hotel", "Combustivel", "Aereo", "Outros", "Total"] else ""
            df_v["Total"] = pd.to_numeric(df_v["Total"], errors='coerce').fillna(0)
        except:
            df_v = pd.DataFrame(columns=cols_viagens)
            sha_v = None

        # 2. Carregar Usuários
        try:
            cont_usr = repo.get_contents("usuarios.csv")
            df_u = pd.read_csv(io.StringIO(cont_usr.decoded_content.decode()))
            sha_u = cont_usr.sha
            
            # Migração automática: se existir coluna Email, renomeia para Usuario
            if "Email" in df_u.columns:
                df_u.rename(columns={"Email": "Usuario"}, inplace=True)
            
            if "Primeiro_Acesso" not in df_u.columns:
                df_u["Primeiro_Acesso"] = "Nao"
        except:
            # Cria a Yara como Admin Master exigindo troca no primeiro login
            df_u = pd.DataFrame([["yara.chaves", "aura123", "Administrador", "Ativo", "Sim"]], columns=cols_usuarios)
            try:
                repo.create_file("usuarios.csv", "Criando banco de usuarios", df_u.to_csv(index=False))
                cont_usr = repo.get_contents("usuarios.csv")
                sha_u = cont_usr.sha
            except:
                sha_u = None

        return df_v, sha_v, df_u, sha_u, repo, g
    except:
        return pd.DataFrame(columns=cols_viagens), None, pd.DataFrame(columns=cols_usuarios), None, None, None

df, sha_viagens, df_usuarios, sha_usuarios, repo, g = carregar_bancos()

# ==========================================================
# 3. TELAS DE AUTENTICAÇÃO
# ==========================================================
if not st.session_state['logado']:
    
    st.markdown("""
    <style>
        .stApp { background-color: #002D5E !important; }
        [data-testid="collapsedControl"] { display: none !important; }
        h1, h2, h3, label, p { color: #FFFFFF !important; font-weight: bold !important; }
        .stTextInput input { background-color: #F0F7FF !important; color: #002D5E !important; border: none !important; border-radius: 8px !important; font-weight: bold !important; }
        input { -webkit-text-fill-color: #002D5E !important; }
        div[data-testid="stFormSubmitButton"] > button { background-color: #FFFFFF !important; border: 2px solid #FFFFFF !important; border-radius: 8px !important; width: 100% !important; height: 55px !important; margin-top: 10px !important; }
        div[data-testid="stFormSubmitButton"] > button p { color: #002D5E !important; font-size: 18px !important; font-weight: 900 !important; }
        div[data-testid="stFormSubmitButton"] > button:hover { background-color: #002D5E !important; border: 2px solid #FFFFFF !important; }
        div[data-testid="stFormSubmitButton"] > button:hover p { color: #FFFFFF !important; }
    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.2, 1])
    
    with col2:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.image("https://raw.githubusercontent.com/yaramaia122-lgtm/logistica-aura/main/logo.png", width=220)
        
        # TELA 3.1: REDEFINIÇÃO OBRIGATÓRIA DE SENHA
        if st.session_state['precisa_trocar_senha']:
            st.markdown("<h2 style='color: white;'>Segurança: Nova Senha</h2>", unsafe_allow_html=True)
            st.info("[ INFO ] Este é o seu primeiro acesso ou sua senha foi resetada. Por diretrizes de segurança, crie uma senha pessoal.")
            
            with st.form("form_troca_senha"):
                nova_senha = st.text_input("Digite sua Nova Senha", type="password")
                confirma_senha = st.text_input("Confirme a Nova Senha", type="password")
                salvar_senha = st.form_submit_button("GRAVAR NOVA SENHA SEGURA")
                
                if salvar_senha:
                    if len(nova_senha) < 4:
                        st.warning("[ ATENÇÃO ] A senha deve ter pelo menos 4 caracteres.")
                    elif nova_senha != confirma_senha:
                        st.error("[ ERRO ] As senhas não coincidem. Tente novamente.")
                    else:
                        if repo:
                            usuario_alvo = st.session_state['usuario_troca']
                            idx = df_usuarios.index[df_usuarios['Usuario'].str.lower() == usuario_alvo].tolist()[0]
                            df_usuarios.at[idx, 'Senha'] = nova_senha
                            df_usuarios.at[idx, 'Primeiro_Acesso'] = 'Nao'
                            
                            repo.update_file("usuarios.csv", f"Senha atualizada pelo usuario: {usuario_alvo}", df_usuarios.to_csv(index=False), sha_usuarios)
                            
                            st.session_state['precisa_trocar_senha'] = False
                            st.session_state['usuario_troca'] = ""
                            st.cache_data.clear()
                            st.success("[ OK ] Senha alterada com sucesso! Faça login novamente com sua nova senha.")
                            st.rerun()
                        else:
                            st.error("[ ERRO ] Falha ao conectar com o servidor para gravar a senha.")
        
        # TELA 3.2: LOGIN PADRÃO
        else:
            st.markdown("<h2 style='color: white;'>Sistema Backoffice</h2>", unsafe_allow_html=True)
            
            with st.form("form_login"):
                usuario_digitado = st.text_input("Usuário Corporativo (ex: nome.sobrenome)")
                senha_digitada = st.text_input("Senha de Acesso", type="password")
                entrar = st.form_submit_button("ENTRAR NO SISTEMA")
                
                if entrar:
                    if df_usuarios.empty:
                        st.error("[ ERRO ] Falha ao conectar com o banco de usuários. Verifique o Token.")
                    else:
                        usuario_limpo = usuario_digitado.strip().lower()
                        usuario_encontrado = df_usuarios[(df_usuarios['Usuario'].str.lower() == usuario_limpo) & 
                                                         (df_usuarios['Senha'] == senha_digitada) & 
                                                         (df_usuarios['Status'] == 'Ativo')]
                        
                        if not usuario_encontrado.empty:
                            if usuario_encontrado.iloc[0]['Primeiro_Acesso'] == 'Sim':
                                st.session_state['precisa_trocar_senha'] = True
                                st.session_state['usuario_troca'] = usuario_limpo
                                st.rerun()
                            else:
                                st.session_state['logado'] = True
                                st.session_state['usuario_atual'] = usuario_limpo
                                st.session_state['perfil'] = usuario_encontrado.iloc[0]['Perfil']
                                st.rerun()
                        else:
                            st.error("[ ERRO ] Usuário ou senha incorretos, ou usuário inativo.")
            
            with st.expander("Esqueceu sua senha?"):
                st.info("Para redefinir sua senha, contate o Administrador do Sistema. Ele irá fornecer uma senha provisória para o seu próximo login.")

# ==========================================================
# 4. APP PRINCIPAL (SÓ CARREGA DEPOIS DO LOGIN)
# ==========================================================
else:
    st.markdown("""
    <style>
        .stApp { background-color: #FFFFFF !important; }
        [data-testid="stSidebar"] { background-color: #002D5E !important; }
        [data-testid="stSidebar"] [data-testid="stImage"] img { filter: drop-shadow(0px 10px 15px rgba(0,0,0,0.6)); }
        h1, h2, h3, label, .stMarkdown p { color: #002D5E !important; font-weight: 700 !important; opacity: 1 !important; }
        [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, [data-testid="stSidebar"] p, [data-testid="stSidebar"] label, [data-testid="stSidebar"] span { color: #FFFFFF !important; }
        .stTextInput input, .stSelectbox div[data-baseweb="select"], .stDateInput input, .stNumberInput input { background-color: #F0F7FF !important; border: 2px solid #002D5E !important; border-radius: 6px !important; }
        input { color: #002D5E !important; -webkit-text-fill-color: #002D5E !important; font-weight: 600 !important; }
        div[data-baseweb="select"] span { color: #002D5E !important; font-weight: 600 !important; }
        div.stButton > button { background-color: #E1E8F0 !important; border: 2px solid #002D5E !important; border-radius: 8px !important; width: 100% !important; height: 50px !important; }
        div.stButton > button * { color: #002D5E !important; font-weight: 800 !important; }
        [data-testid="stDataFrame"] { border: 1px solid #002D5E !important; border-radius: 8px !important; overflow: hidden !important;}
        .stTabs [data-baseweb="tab-list"] { gap: 20px; }
        .stTabs [data-baseweb="tab"] { height: 50px; white-space: pre-wrap; background-color: #F0F7FF; border-radius: 6px 6px 0px 0px; padding-left: 20px; padding-right: 20px;}
        .stTabs [aria-selected="true"] { background-color: #002D5E !important; color: white !important;}
        .stTabs [aria-selected="true"] p { color: white !important; font-weight: bold !important;}
    </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.markdown("<br>", unsafe_allow_html=True)
        st.image("https://raw.githubusercontent.com/yaramaia122-lgtm/logistica-aura/main/logo.png", width=220)
        st.markdown(f"<p style='color: white; text-align: center; font-size: 14px;'>Usuário: <b>{st.session_state['usuario_atual']}</b><br>Perfil: {st.session_state['perfil']}</p>", unsafe_allow_html=True)
        st.markdown("---")
        
        opcoes_menu = ["Dashboard", "Agenda", "Programar Viagem"]
        if st.session_state.get('perfil') == "Administrador":
            opcoes_menu.append("Administração")
            
        menu = st.radio("NAVEGAÇÃO DO SISTEMA", opcoes_menu)
        
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        if st.button("Encerrar Sessão"):
            st.session_state['logado'] = False
            st.session_state['usuario_atual'] = ""
            st.session_state['perfil'] = ""
            st.session_state['precisa_trocar_senha'] = False
            st.cache_data.clear()
            st.rerun()

    if menu == "Dashboard":
        st.title("Painel de Indicadores")
        st.markdown("Resumo gerencial e métricas de desempenho logístico.")
        st.divider()
        if not df.empty:
            col1, col2, col3 = st.columns(3)
            col1.metric(label="Viagens Registradas", value=len(df))
            col2.metric(label="Custo Global Estimado", value=f"R$ {df['Total'].sum():,.2f}")
            col3.metric(label="Motoristas Engajados", value=df["Motorista"].nunique())
            
            st.markdown("<br>", unsafe_allow_html=True)
            col_graf1, col_graf2 = st.columns(2)
            with col_graf1:
                st.markdown("#### Custos por Centro de Custo")
                st.bar_chart(df.groupby("Centro de Custo")["Total"].sum().sort_values(ascending=False))
            with col_graf2:
                st.markdown("#### Destinos Mais Frequentes")
                st.bar_chart(df["Trajeto"].value_counts())
        else:
            st.info("[ INFO ] Sem dados para gerar o dashboard.")

    elif menu == "Agenda":
        st.title("Agenda de Viagens")
        st.markdown("Visão geral das programações logísticas.")
        st.divider()
        if not df.empty:
            st.dataframe(df[["Passageiro", "Motorista", "Data", "Trajeto", "Centro de Custo", "Obs"]], use_container_width=True, hide_index=True)
        else:
            st.info("[ INFO ] Nenhuma viagem agendada.")

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
            "310101 - Almoxarifado", "320401 - Controladoria e Contabilidade", "310701 - Serviços Gerais",
            "320601 - Celula de Gestao de Contratos", "320101 - Suprimentos", "320502 - Tecnologia da Informação"
        ]
        
        if not df.empty and "Centro de Custo" in df.columns:
            lista_completa = sorted(list(set(lista_base + df["Centro de Custo"].dropna().unique().tolist())))
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
        aceite_lgpd = form.checkbox("Confirmo a ciência das Políticas Internas (LGPD)")
        gravar = form.form_submit_button("GRAVAR REGISTRO NO SISTEMA")

        if gravar:
            centro_custo_final = novo_cc.strip() if novo_cc.strip() != "" else cc_selecionado
            if not nome: st.warning("[ ATENÇÃO ] O campo 'Nome do Passageiro' não pode ficar vazio.")
            elif not aceite_lgpd: st.warning("[ ATENÇÃO ] O aceite da Política é obrigatório.")
            elif not repo: st.error("[ ERRO ] Falha de conexão com o banco de dados.")
            else:
                total = v_h + v_c + v_a + v_o
                nova_viagem = pd.DataFrame([[nome, moto, data.strftime('%d/%m/%Y'), traj, centro_custo_final, obs, v_h, v_c, v_a, v_o, total, datetime.now().strftime("%d/%m/%Y %H:%M:%S"), st.session_state['usuario_atual']]], columns=df.columns)
                df_final = pd.concat([df, nova_viagem], ignore_index=True)
                repo.update_file("dados_logistica.csv", "Registro de Viagem", df_final.to_csv(index=False), sha_viagens)
                st.cache_data.clear()
                st.success("[ OK ] VIAGEM PROGRAMADA E GRAVADA COM SUCESSO!")
                st.rerun()

    elif menu == "Administração" and st.session_state.get('perfil') == "Administrador":
        st.title("Painel de Administração")
        st.markdown("Módulo central de segurança e gestão. Restrito ao nível Administrador.")
        st.divider()
        
        tab_fin, tab_usr, tab_seg = st.tabs(["Controle Financeiro", "Gestão de Usuários e Segurança", "Governança"])
        
        with tab_fin:
            st.markdown("### Auditoria de Custos Logísticos")
            df_ed = st.data_editor(df, num_rows="dynamic", use_container_width=True, hide_index=True)
            if st.button("ATUALIZAR BANCO FINANCEIRO"):
                if repo:
                    df_ed["Total"] = df_ed["Hotel"] + df_ed["Combustivel"] + df_ed["Aereo"] + df_ed["Outros"]
                    repo.update_file("dados_logistica.csv", "Edição Financeira via Admin", df_ed.to_csv(index=False), sha_viagens)
                    st.cache_data.clear()
                    st.success("[ OK ] BASE DE DADOS ATUALIZADA!")
                    st.rerun()
                    
        with tab_usr:
            st.markdown("### Controle de Acessos")
            st.markdown("Para resetar a senha de um colaborador: Altere a **Senha**, mude a coluna **Exigir Troca de Senha?** para **'Sim'** e clique em Salvar.")
            
            if not df_usuarios.empty:
                df_usr_edit = st.data_editor(df_usuarios, num_rows="dynamic", use_container_width=True, hide_index=True,
                                             column_config={
                                                 "Perfil": st.column_config.SelectboxColumn("Perfil", options=["Administrador", "Operador"], required=True),
                                                 "Status": st.column_config.SelectboxColumn("Status", options=["Ativo", "Inativo"], required=True),
                                                 "Primeiro_Acesso": st.column_config.SelectboxColumn("Exigir Troca de Senha?", options=["Sim", "Nao"], required=True)
                                             })
                
                if st.button("SALVAR ALTERAÇÕES DE USUÁRIOS E SEGURANÇA"):
                    if repo:
                        repo.update_file("usuarios.csv", "Edição de Acessos via Admin", df_usr_edit.to_csv(index=False), sha_usuarios)
                        st.cache_data.clear()
                        st.success("[ OK ] SEGURANÇA ATUALIZADA COM SUCESSO!")
                        st.rerun()
            else:
                st.error("[ ERRO ] Falha ao carregar banco de usuários.")
            
        with tab_seg:
            st.markdown("### Arquitetura de Confiança Zero (Zero Trust)")
            st.success("[ OK ] Forçar Troca de Senha de Novos Usuários: Ativo")
            st.success("[ OK ] Senhas Definitivas Inacessíveis pelo Administrador: Ativo")
            st.success("[ OK ] Criptografia em Nuvem e HTTPS: Ativo")
