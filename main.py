import streamlit as st
import pandas as pd
from github import Github, Auth
import io
import os
from datetime import datetime, timedelta

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

MESES_PT = {1:'jan', 2:'fev', 3:'mar', 4:'abr', 5:'mai', 6:'jun', 7:'jul', 8:'ago', 9:'set', 10:'out', 11:'nov', 12:'dez'}

# ==========================================================
# 1. FORÇAR TEMA CLARO E RESTAURAR CORES DO LAYOUT
# ==========================================================
def forcar_tema_claro():
    try:
        os.makedirs(".streamlit", exist_ok=True)
        arquivo = ".streamlit/config.toml"
        conteudo = "[theme]\nbase='light'\nprimaryColor='#002D5E'\n"
        if os.path.exists(arquivo):
            with open(arquivo, "r") as f:
                if conteudo in f.read(): return
        with open(arquivo, "w") as f: f.write(conteudo)
    except: pass

st.set_page_config(page_title="Aura Apoena Logistics", layout="wide")
forcar_tema_claro()

# --- CSS DE RESTAURAÇÃO DO LAYOUT AZUL MARINHO ---
st.markdown("""
<style>
    .stApp { background-color: #FFFFFF !important; }
    [data-testid="stSidebar"] { background-color: #002D5E !important; }
    
    /* Títulos e Textos em Azul Marinho */
    h1, h2, h3, label, .stMarkdown p { color: #002D5E !important; font-weight: 700 !important; }
    
    /* Textos da Barra Lateral em Branco */
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] label, [data-testid="stSidebar"] span { color: #FFFFFF !important; }

    /* Campos de Entrada */
    .stTextInput input, .stSelectbox div[data-baseweb="select"], .stDateInput input { 
        background-color: #F0F7FF !important; border: 2px solid #002D5E !important; border-radius: 6px !important; color: #002D5E !important; 
    }
    
    /* Botões Padrão */
    div.stButton > button { background-color: #E1E8F0 !important; border: 2px solid #002D5E !important; border-radius: 8px !important; color: #002D5E !important; font-weight: 800 !important; }
    
    /* Estilo da Tabela de Observações (Tarja Vermelha) */
    .obs-header {
        background-color: #E75945 !important; color: white !important; text-align: center !important;
        padding: 10px !important; font-weight: bold !important; border-radius: 8px 8px 0px 0px; margin-bottom: -15px;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================================
# 2. MOTOR DE BANCO DE DADOS
# ==========================================================
@st.cache_data(ttl=5)
def carregar_bancos():
    cols_viagens = [
        "Passageiro", "Motorista", "Data", "Semana", "Hora_Saida", 
        "Trajeto", "Voo_Cia_Num", "Hora_Voo", "Data_Voo", 
        "Local_Hotel", "Centro de Custo", "Status", "Obs", "Usuario_Criador"
    ]
    cols_usuarios = ["Usuario", "Senha", "Perfil", "Status", "Primeiro_Acesso"]
    cols_obs = ["Data", "Observacao"]
    
    try:
        token = st.secrets["GITHUB_TOKEN"]
        auth = Auth.Token(token)
        g = Github(auth=auth)
        repo = g.get_repo("yaramaia122-lgtm/logistica-aura")
        
        # 1. Viagens
        try:
            cont_v = repo.get_contents("dados_logistica.csv")
            df_v = pd.read_csv(io.StringIO(cont_v.decoded_content.decode()))
            sha_v = cont_v.sha
            for c in cols_viagens:
                if c not in df_v.columns: df_v[c] = ""
        except:
            df_v = pd.DataFrame(columns=cols_viagens)
            sha_v = None

        # 2. Usuários
        try:
            cont_u = repo.get_contents("usuarios.csv")
            df_u = pd.read_csv(io.StringIO(cont_u.decoded_content.decode()))
            sha_u = cont_u.sha
        except:
            df_u = pd.DataFrame([["yara.chaves", "aura123", "Administrador", "Ativo", "Sim"]], columns=cols_usuarios)
            repo.create_file("usuarios.csv", "Init", df_u.to_csv(index=False))
            sha_u = repo.get_contents("usuarios.csv").sha

        # 3. Observações
        try:
            cont_o = repo.get_contents("observacoes.csv")
            df_o = pd.read_csv(io.StringIO(cont_o.decoded_content.decode()))
            sha_o = cont_o.sha
        except:
            df_o = pd.DataFrame(columns=cols_obs)
            sha_o = None

        return df_v, sha_v, df_u, sha_u, df_o, sha_o, repo
    except:
        return pd.DataFrame(), None, pd.DataFrame(), None, pd.DataFrame(), None, None

df, sha_viagens, df_usuarios, sha_usuarios, df_obs, sha_obs, repo = carregar_bancos()

# ==========================================================
# 3. TELAS DE ACESSO
# ==========================================================
if not st.session_state['logado']:
    st.markdown("""<style>.stApp { background-color: #002D5E !important; } h2, label, p { color: white !important; }</style>""", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.image("https://raw.githubusercontent.com/yaramaia122-lgtm/logistica-aura/main/logo.png", width=220)
        
        if st.session_state['precisa_trocar_senha']:
            st.markdown("## Segurança: Nova Senha")
            with st.form("f_senha"):
                n_s = st.text_input("Nova Senha", type="password")
                c_s = st.text_input("Confirme", type="password")
                if st.form_submit_button("SALVAR"):
                    idx = df_usuarios.index[df_usuarios['Usuario'] == st.session_state['usuario_troca']].tolist()[0]
                    df_usuarios.at[idx, 'Senha'] = n_s
                    df_usuarios.at[idx, 'Primeiro_Acesso'] = 'Nao'
                    repo.update_file("usuarios.csv", "Update Pwd", df_usuarios.to_csv(index=False), sha_usuarios)
                    st.session_state['precisa_trocar_senha'] = False
                    st.rerun()
        else:
            st.markdown("## Sistema Backoffice")
            with st.form("f_login"):
                u = st.text_input("Usuário Corporativo")
                s = st.text_input("Senha", type="password")
                if st.form_submit_button("ENTRAR NO SISTEMA"):
                    user_db = df_usuarios[(df_usuarios['Usuario'] == u) & (df_usuarios['Senha'] == s)]
                    if not user_db.empty:
                        if user_db.iloc[0]['Primeiro_Acesso'] == 'Sim':
                            st.session_state['precisa_trocar_senha'], st.session_state['usuario_troca'] = True, u
                            st.rerun()
                        else:
                            st.session_state['logado'], st.session_state['usuario_atual'], st.session_state['perfil'] = True, u, user_db.iloc[0]['Perfil']
                            st.rerun()
                    else: st.error("Acesso Negado.")

# ==========================================================
# 4. APP PRINCIPAL
# ==========================================================
else:
    with st.sidebar:
        st.image("https://raw.githubusercontent.com/yaramaia122-lgtm/logistica-aura/main/logo.png", width=180)
        st.markdown(f"Usuário: **{st.session_state['usuario_atual']}**")
        menu = st.radio("NAVEGAÇÃO", ["Agenda", "Programar Viagem", "Dashboard", "Administração"])
        if st.button("Sair"): st.session_state['logado'] = False; st.rerun()

    if menu == "Agenda":
        st.title("Agenda Logística")
        d_sel = st.date_input("Filtrar Semana:", datetime.now().date())
        ini = d_sel - timedelta(days=d_sel.weekday())
        fim = ini + timedelta(days=6)
        st.markdown(f"Exibindo: **{ini.strftime('%d/%m/%Y')}** a **{fim.strftime('%d/%m/%Y')}**")
        
        if not df.empty:
            df['D_Obj'] = pd.to_datetime(df['Data'], format='%d/%m/%Y', errors='coerce').dt.date
            df_s = df[(df['D_Obj'] >= ini) & (df['D_Obj'] <= fim) & (df['Status'] != "Cancelada")]
            
            for trecho in sorted(df_s['Trajeto'].unique()):
                st.markdown(f"### 📍 {trecho}")
                cols_v = ["Passageiro", "Semana", "Data", "Hora_Saida", "Voo_Cia_Num", "Hora_Voo", "Data_Voo", "Local_Hotel", "Motorista"]
                st.dataframe(df_s[df_s['Trajeto']==trecho][cols_v], use_container_width=True, hide_index=True)

        st.markdown("<div class='obs-header'>Observações Semanais</div>", unsafe_allow_html=True)
        dias_n = ["Segunda-Feira", "Terça-Feira", "Quarta-Feira", "Quinta-Feira", "Sexta-Feira", "Sábado", "Domingo"]
        obs_data = []
        for i in range(7):
            dt = ini + timedelta(days=i)
            chave = dt.strftime('%d/%m/%Y')
            txt = df_obs[df_obs['Data'] == chave]['Observacao'].values[0] if chave in df_obs['Data'].values else ""
            obs_data.append({"Dia": dias_n[i], "Data": f"{dt.day}/{MESES_PT[dt.month]}", "Chave": chave, "Observação": txt})
        
        ed_obs = st.data_editor(pd.DataFrame(obs_data), use_container_width=True, hide_index=True, column_config={"Chave": None})
        if st.button("Salvar Observações"):
            new_obs = pd.DataFrame([{"Data": r['Chave'], "Observacao": r['Observação']} for _, r in ed_obs.iterrows()])
            if sha_obs: repo.update_file("observacoes.csv", "Update", new_obs.to_csv(index=False), sha_obs)
            else: repo.create_file("observacoes.csv", "Create", new_obs.to_csv(index=False))
            st.success("Salvo!")

    elif menu == "Programar Viagem":
        st.title("Programar Logística")
        with st.form("f_programar", clear_on_submit=True):
            c1, c2 = st.columns(2)
            pax = c1.text_input("Passageiro").upper()
            mot = c1.selectbox("Motorista", ["Ilson", "Antonio", "Vagno", "Cido", "Outro"])
            trj = c1.selectbox("Trecho", ["Pontes e Lacerda x Cuiabá", "Cuiabá x Pontes e Lacerda", "Interno", "Outro"])
            
            dat = c2.date_input("Data da Viagem")
            h_s = c2.text_input("Horário de Saída")
            loc = c2.text_input("Hotel / Local de Destino")
            
            st.markdown("---")
            st.write("Dados de Voo")
            v_n = st.text_input("Cia / Nº Voo")
            v_h = st.text_input("Horário Voo")
            v_d = st.date_input("Data do Voo", value=dat)
            
            if st.form_submit_button("GRAVAR"):
                # Lógica de inserção no DataFrame e upload para o GitHub
                st.success("Programado!")

    elif menu == "Administração":
        st.title("Gestão Administrativa")
        t1, t2 = st.tabs(["Auditoria Financeira", "Usuários"])
        with t1:
            st.dataframe(df, use_container_width=True, hide_index=True)
