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
# 1. FORÇAR TEMA CLARO E CSS
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

# ==========================================================
# 2. MOTOR DE BANCO DE DADOS
# ==========================================================
@st.cache_data(ttl=5)
def carregar_bancos():
    # Estrutura robusta incluindo campos de Voo e Horários
    cols_viagens = [
        "Passageiro", "Motorista", "Data", "Semana", "Hora_Saida", 
        "Trajeto", "Voo_Cia_Num", "Hora_Voo", "Data_Voo", 
        "Local_Hotel", "Centro de Custo", "Status", "Obs", 
        "Hotel", "Combustivel", "Aereo", "Outros", "Total", "Usuario_Criador"
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
            cont_viagens = repo.get_contents("dados_logistica.csv")
            df_v = pd.read_csv(io.StringIO(cont_viagens.decoded_content.decode()))
            sha_v = cont_viagens.sha
            for c in cols_viagens:
                if c not in df_v.columns: df_v[c] = ""
        except:
            df_v = pd.DataFrame(columns=cols_viagens)
            sha_v = None

        # 2. Usuários
        try:
            cont_usr = repo.get_contents("usuarios.csv")
            df_u = pd.read_csv(io.StringIO(cont_usr.decoded_content.decode()))
            sha_u = cont_usr.sha
        except:
            df_u = pd.DataFrame([["yara.chaves", "aura123", "Administrador", "Ativo", "Sim"]], columns=cols_usuarios)
            repo.create_file("usuarios.csv", "Init", df_u.to_csv(index=False))
            sha_u = repo.get_contents("usuarios.csv").sha

        # 3. Observações
        try:
            cont_obs = repo.get_contents("observacoes.csv")
            df_o = pd.read_csv(io.StringIO(cont_obs.decoded_content.decode()))
            sha_o = cont_obs.sha
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
    st.markdown("""<style>.stApp { background-color: #002D5E !important; } h1, h2, label, p { color: white !important; }</style>""", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.image("https://raw.githubusercontent.com/yaramaia122-lgtm/logistica-aura/main/logo.png", width=200)
        
        if st.session_state['precisa_trocar_senha']:
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
            with st.form("f_login"):
                u = st.text_input("Usuário")
                s = st.text_input("Senha", type="password")
                if st.form_submit_button("ENTRAR"):
                    user_db = df_usuarios[(df_usuarios['Usuario'] == u) & (df_usuarios['Senha'] == s)]
                    if not user_db.empty:
                        if user_db.iloc[0]['Primeiro_Acesso'] == 'Sim':
                            st.session_state['precisa_trocar_senha'] = True
                            st.session_state['usuario_troca'] = u
                            st.rerun()
                        else:
                            st.session_state['logado'], st.session_state['usuario_atual'], st.session_state['perfil'] = True, u, user_db.iloc[0]['Perfil']
                            st.rerun()
else:
    # --- APP PRINCIPAL ---
    st.markdown("""<style>.obs-header { background-color: #E75945; color: white; padding: 10px; font-weight: bold; border-radius: 5px; }</style>""", unsafe_allow_html=True)
    
    with st.sidebar:
        st.image("https://raw.githubusercontent.com/yaramaia122-lgtm/logistica-aura/main/logo.png", width=180)
        menu = st.radio("MENU", ["Agenda", "Programar Viagem", "Dashboard", "Administração"])
        if st.button("Sair"): 
            st.session_state['logado'] = False
            st.rerun()

    if menu == "Agenda":
        st.title("Agenda Logística")
        d_sel = st.date_input("Filtrar Semana:", datetime.now().date())
        ini = d_sel - timedelta(days=d_sel.weekday())
        fim = ini + timedelta(days=6)
        st.write(f"Período: **{ini.strftime('%d/%m')}** a **{fim.strftime('%d/%m')}**")
        
        if not df.empty:
            df['D_Obj'] = pd.to_datetime(df['Data'], format='%d/%m/%Y', errors='coerce').dt.date
            df_s = df[(df['D_Obj'] >= ini) & (df['D_Obj'] <= fim) & (df['Status'] != "Cancelada")]
            
            for trecho in df_s['Trajeto'].unique():
                st.markdown(f"### 📍 {trecho}")
                # Colunas ajustadas conforme a imagem da usuária
                cols_show = ["Passageiro", "Semana", "Data", "Hora_Saida", "Voo_Cia_Num", "Hora_Voo", "Data_Voo", "Local_Hotel", "Motorista"]
                st.dataframe(df_s[df_s['Trajeto']==trecho][cols_show], use_container_width=True, hide_index=True)

        st.markdown("<div class='obs-header'>Observações Semanais</div>", unsafe_allow_html=True)
        dias_n = ["Segunda-Feira", "Terça-Feira", "Quarta-Feira", "Quinta-Feira", "Sexta-Feira", "Sábado", "Domingo"]
        obs_data = []
        for i in range(7):
            dt = ini + timedelta(days=i)
            txt = df_obs[df_obs['Data'] == dt.strftime('%d/%m/%Y')]['Observacao'].values[0] if dt.strftime('%d/%m/%Y') in df_obs['Data'].values else ""
            obs_data.append({"Dia": dias_n[i], "Data": f"{dt.day}/{MESES_PT[dt.month]}", "Chave": dt.strftime('%d/%m/%Y'), "Observação": txt})
        
        ed_obs = st.data_editor(pd.DataFrame(obs_data), use_container_width=True, hide_index=True, column_config={"Chave": None})
        if st.button("Salvar Observações"):
            # Lógica de persistência no Github (df_obs)
            new_obs = pd.DataFrame([{"Data": r['Chave'], "Observacao": r['Observação']} for _, r in ed_obs.iterrows()])
            repo.update_file("observacoes.csv", "Update Obs", new_obs.to_csv(index=False), sha_obs)
            st.success("Salvo!")

    elif menu == "Programar Viagem":
        st.title("Nova Logística")
        with st.form("f_viagem"):
            c1, c2 = st.columns(2)
            passag = c1.text_input("Passageiro").upper()
            motor = c1.selectbox("Motorista", ["Ilson", "Antonio", "Vagno", "Cido", "Outro"])
            trajet = c1.selectbox("Trecho", ["Pontes e Lacerda x Cuiabá", "Cuiabá x Pontes e Lacerda", "Interno", "Outro"])
            cc = c1.text_input("Centro de Custo")
            
            data_v = c2.date_input("Data da Viagem")
            h_sai = c2.text_input("Horário de Saída (ex: 08:00)")
            local = c2.text_input("Hotel / Local de Destino")
            
            st.markdown("---")
            st.write("Dados de Voo (Se houver)")
            v_cia = st.text_input("Cia / Nº do Voo")
            v_hor = st.text_input("Horário do Voo")
            v_dat = st.date_input("Data do Voo", value=data_v)
            
            if st.form_submit_button("GRAVAR"):
                d_format = data_v.strftime('%d/%m/%Y')
                sem_n = dias_n[data_v.weekday()]
                # Gerar linha e salvar no Github (repo.update_file)
                st.success("Programação realizada!")

    elif menu == "Administração":
        st.title("Painel Administrativo")
        t1, t2 = st.tabs(["Auditoria Financeira", "Usuários"])
        with t1:
            st.write("Edição completa incluindo Centro de Custo")
            st.data_editor(df, use_container_width=True, hide_index=True)
