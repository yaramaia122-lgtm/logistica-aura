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
DIAS_SEMANA_PT = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"]

# ==========================================================
# 1. TEMA E CSS (LAYOUT CORPORATIVO AZUL MARINHO)
# ==========================================================
def forcar_tema_claro():
    try:
        os.makedirs(".streamlit", exist_ok=True)
        arquivo = ".streamlit/config.toml"
        conteudo = "[theme]\nbase='light'\nprimaryColor='#002D5E'\n"
        if not os.path.exists(arquivo):
            with open(arquivo, "w") as f: f.write(conteudo)
    except: pass

st.set_page_config(page_title="Aura Apoena Logistics", layout="wide")
forcar_tema_claro()

st.markdown("""
<style>
    .stApp { background-color: #FFFFFF !important; }
    [data-testid="stSidebar"] { background-color: #002D5E !important; }
    h1, h2, h3, label, .stMarkdown p { color: #002D5E !important; font-weight: 700 !important; }
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] label, [data-testid="stSidebar"] span { color: #FFFFFF !important; }
    .stTextInput input, .stSelectbox div[data-baseweb="select"], .stDateInput input, .stNumberInput input { 
        background-color: #F0F7FF !important; border: 2px solid #002D5E !important; border-radius: 6px !important; color: #002D5E !important; 
    }
    div.stButton > button { background-color: #E1E8F0 !important; border: 2px solid #002D5E !important; border-radius: 8px !important; color: #002D5E !important; font-weight: 800 !important; }
    .obs-header { background-color: #E75945 !important; color: white !important; text-align: center !important; padding: 10px !important; font-weight: bold !important; border-radius: 8px 8px 0px 0px; margin-bottom: -15px; }
</style>
""", unsafe_allow_html=True)

# ==========================================================
# 2. MOTOR DE BANCO DE DADOS (GERENCIAMENTO DE ARQUIVOS)
# ==========================================================
@st.cache_data(ttl=5)
def carregar_bancos():
    cols_v = ["Passageiro", "Motorista", "Data", "Semana", "Hora_Saida", "Trajeto", "Voo_Cia_Num", "Hora_Voo", "Data_Voo", "Local_Hotel", "Centro de Custo", "Status", "Hotel_Valor", "Combustivel_Valor", "Aereo_Valor", "Outros_Valor", "Total", "Usuario_Criador"]
    cols_u = ["Usuario", "Senha", "Perfil", "Status", "Primeiro_Acesso"]
    
    try:
        token = st.secrets["GITHUB_TOKEN"]
        auth = Auth.Token(token)
        g = Github(auth=auth)
        repo = g.get_repo("yaramaia122-lgtm/logistica-aura")
        
        # --- CARREGAR VIAGENS ---
        try:
            cont_v = repo.get_contents("dados_logistica.csv")
            df_v = pd.read_csv(io.StringIO(cont_v.decoded_content.decode()))
            sha_v = cont_v.sha
            for c in cols_v:
                if c not in df_v.columns: df_v[c] = 0.0 if "_Valor" in c or c == "Total" else ""
        except:
            df_v = pd.DataFrame(columns=cols_v); sha_v = None

        # --- CARREGAR USUÁRIOS (RECUPERAÇÃO DE ACESSO) ---
        try:
            cont_u = repo.get_contents("usuarios.csv")
            df_u = pd.read_csv(io.StringIO(cont_u.decoded_content.decode()))
            sha_u = cont_u.sha
            # Migração de colunas Email -> Usuario
            if "Email" in df_u.columns: df_u.rename(columns={"Email": "Usuario"}, inplace=True)
            # Garantir Yara mestre
            if "yara.chaves" not in df_u["Usuario"].values:
                nova = pd.DataFrame([["yara.chaves", "aura123", "Administrador", "Ativo", "Sim"]], columns=cols_u)
                df_u = pd.concat([df_u, nova], ignore_index=True)
                repo.update_file("usuarios.csv", "Fix Yara", df_u.to_csv(index=False), sha_u)
                sha_u = repo.get_contents("usuarios.csv").sha
        except:
            df_u = pd.DataFrame([["yara.chaves", "aura123", "Administrador", "Ativo", "Sim"]], columns=cols_u)
            repo.create_file("usuarios.csv", "Init Usr", df_u.to_csv(index=False))
            sha_u = repo.get_contents("usuarios.csv").sha

        # --- CARREGAR OBSERVAÇÕES ---
        try:
            cont_o = repo.get_contents("observacoes.csv")
            df_o = pd.read_csv(io.StringIO(cont_o.decoded_content.decode()))
            sha_o = cont_o.sha
        except:
            df_o = pd.DataFrame(columns=["Data", "Observacao"]); sha_o = None

        return df_v, sha_v, df_u, sha_u, df_o, sha_o, repo
    except: return pd.DataFrame(), None, pd.DataFrame(), None, pd.DataFrame(), None, None

df, sha_viagens, df_usuarios, sha_usuarios, df_obs, sha_obs, repo = carregar_bancos()

# ==========================================================
# 3. AUTENTICAÇÃO (LOGIN)
# ==========================================================
if not st.session_state['logado']:
    st.markdown("""<style>.stApp { background-color: #002D5E !important; } h2, label, p { color: white !important; }</style>""", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.image("https://raw.githubusercontent.com/yaramaia122-lgtm/logistica-aura/main/logo.png", width=220)
        
        if st.session_state['precisa_trocar_senha']:
            with st.form("f_pwd"):
                n_s = st.text_input("Nova Senha", type="password")
                c_s = st.text_input("Confirme Senha", type="password")
                if st.form_submit_button("SALVAR SENHA"):
                    if n_s == c_s:
                        idx = df_usuarios.index[df_usuarios['Usuario'] == st.session_state['usuario_troca']].tolist()[0]
                        df_usuarios.at[idx, 'Senha'] = n_s
                        df_usuarios.at[idx, 'Primeiro_Acesso'] = 'Nao'
                        repo.update_file("usuarios.csv", "Pwd Change", df_usuarios.to_csv(index=False), sha_usuarios)
                        st.session_state['precisa_trocar_senha'] = False
                        st.success("Pronto! Faça login novamente.")
                        st.rerun()
        else:
            with st.form("f_log"):
                u = st.text_input("Usuário Corporativo (yara.chaves)")
                s = st.text_input("Senha", type="password")
                if st.form_submit_button("ENTRAR"):
                    u_db = df_usuarios[(df_usuarios['Usuario'] == u) & (df_usuarios['Senha'] == s)]
                    if not u_db.empty:
                        if u_db.iloc[0]['Primeiro_Acesso'] == 'Sim':
                            st.session_state['precisa_trocar_senha'], st.session_state['usuario_troca'] = True, u
                            st.rerun()
                        else:
                            st.session_state['logado'], st.session_state['usuario_atual'], st.session_state['perfil'] = True, u, u_db.iloc[0]['Perfil']
                            st.rerun()
                    else: st.error("Incorreto.")

# ==========================================================
# 4. APP PRINCIPAL
# ==========================================================
else:
    with st.sidebar:
        st.image("https://raw.githubusercontent.com/yaramaia122-lgtm/logistica-aura/main/logo.png", width=180)
        st.write(f"Logado: **{st.session_state['usuario_atual']}**")
        menu = st.radio("NAVEGAÇÃO", ["Agenda", "Programar Viagem", "Administração"])
        if st.button("Sair"): st.session_state['logado'] = False; st.rerun()

    if menu == "Agenda":
        st.title("Agenda Logística")
        d_sel = st.date_input("Semana:", datetime.now().date())
        ini = d_sel - timedelta(days=d_sel.weekday())
        fim = ini + timedelta(days=6)
        
        if not df.empty:
            df['D_Obj'] = pd.to_datetime(df['Data'], format='%d/%m/%Y', errors='coerce').dt.date
            df_s = df[(df['D_Obj'] >= ini) & (df['D_Obj'] <= fim) & (df['Status'] != "Cancelada")]
            for t in sorted(df_s['Trajeto'].unique()):
                st.markdown(f"### 📍 {t}")
                st.dataframe(df_s[df_s['Trajeto']==t][["Passageiro", "Semana", "Data", "Hora_Saida", "Voo_Cia_Num", "Hora_Voo", "Data_Voo", "Local_Hotel", "Motorista"]], use_container_width=True, hide_index=True)

        st.markdown("<div class='obs-header'>Observações Semanais</div>", unsafe_allow_html=True)
        obs_l = []
        for i in range(7):
            dt = ini + timedelta(days=i)
            ch = dt.strftime('%d/%m/%Y')
            tx = df_obs[df_obs['Data'] == ch]['Observacao'].values[0] if ch in df_obs['Data'].values else ""
            obs_l.append({"Dia": DIAS_SEMANA_PT[i], "Data": f"{dt.day}/{MESES_PT[dt.month]}", "Chave": ch, "Observação": tx})
        
        ed_obs = st.data_editor(pd.DataFrame(obs_l), use_container_width=True, hide_index=True, column_config={"Chave": None})
        if st.button("Salvar Observações"):
            new_o = pd.DataFrame([{"Data": r['Chave'], "Observacao": r['Observação']} for _, r in ed_obs.iterrows()])
            repo.update_file("observacoes.csv", "Upd", new_o.to_csv(index=False), sha_obs)
            st.cache_data.clear(); st.success("Salvo!"); st.rerun()

    elif menu == "Programar Viagem":
        st.title("Nova Programação")
        with st.form("f_add", clear_on_submit=True):
            c1, c2 = st.columns(2)
            px = c1.text_input("Passageiro").upper()
            mt = c1.selectbox("Motorista", ["Ilson", "Antonio", "Vagno", "Cido", "Outro"])
            tj = c1.selectbox("Trecho", ["Pontes e Lacerda x Cuiabá", "Cuiabá x Pontes e Lacerda", "Interno", "Outro"])
            cc = c1.text_input("Centro de Custo")
            
            dt = c2.date_input("Data")
            hs = c2.text_input("Saída")
            lh = c2.text_input("Hotel/Destino")
            
            st.markdown("---")
            vn = st.text_input("Cia/Voo")
            vh = st.text_input("Hora Voo")
            vd = st.date_input("Data Voo", value=dt)
            
            st.markdown("---")
            vh_v = st.number_input("Custo Hotel (R$)")
            va_v = st.number_input("Custo Aéreo (R$)")
            vc_v = st.number_input("Custo Combustível (R$)")
            vo_v = st.number_input("Outros (R$)")
            
            if st.form_submit_button("GRAVAR"):
                sem = DIAS_SEMANA_PT[dt.weekday()]
                tot = vh_v + va_v + vc_v + vo_v
                nova = {
                    "Passageiro": px, "Motorista": mt, "Data": dt.strftime('%d/%m/%Y'),
                    "Semana": sem, "Hora_Saida": hs, "Trajeto": tj,
                    "Voo_Cia_Num": vn, "Hora_Voo": vh, "Data_Voo": vd.strftime('%d/%m/%Y'),
                    "Local_Hotel": lh, "Centro de Custo": cc, "Status": "Confirmada",
                    "Hotel_Valor": vh_v, "Aereo_Valor": va_v, "Combustivel_Valor": vc_v, 
                    "Outros_Valor": vo_v, "Total": tot, "Usuario_Criador": st.session_state['usuario_atual']
                }
                df_f = pd.concat([df, pd.DataFrame([nova])], ignore_index=True)
                repo.update_file("dados_logistica.csv", "Add", df_f.to_csv(index=False), sha_viagens)
                st.cache_data.clear(); st.success("Gravado!"); st.rerun()

    elif menu == "Administração":
        st.title("Painel de Administração")
        tab1, tab2 = st.tabs(["Auditoria de Viagens", "Gestão de Usuários"])
        
        with tab1:
            st.markdown("### Controle Financeiro e Status")
            df_ed = st.data_editor(df, use_container_width=True, hide_index=True, 
                                   column_config={"Status": st.column_config.SelectboxColumn("Status", options=["Confirmada", "Realizada", "Cancelada"])})
            if st.button("Salvar Viagens"):
                df_ed["Total"] = df_ed["Hotel_Valor"] + df_ed["Aereo_Valor"] + df_ed["Combustivel_Valor"] + df_ed["Outros_Valor"]
                repo.update_file("dados_logistica.csv", "Adm Edit", df_ed.to_csv(index=False), sha_viagens)
                st.cache_data.clear(); st.success("Banco de Viagens Atualizado!"); st.rerun()
                
        with tab2:
            st.markdown("### Gestão de Acessos e Senhas")
            df_u_ed = st.data_editor(df_usuarios, use_container_width=True, hide_index=True,
                                     column_config={
                                         "Perfil": st.column_config.SelectboxColumn("Perfil", options=["Administrador", "Operador"]),
                                         "Status": st.column_config.SelectboxColumn("Status", options=["Ativo", "Inativo"]),
                                         "Primeiro_Acesso": st.column_config.SelectboxColumn("Exigir Troca Senha?", options=["Sim", "Nao"])
                                     })
            if st.button("Salvar Usuários"):
                repo.update_file("usuarios.csv", "Usr Edit", df_u_ed.to_csv(index=False), sha_usuarios)
                st.cache_data.clear(); st.success("Banco de Usuários Atualizado!"); st.rerun()
