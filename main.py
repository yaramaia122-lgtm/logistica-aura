import streamlit as st
import pandas as pd
from github import Github, Auth
import io
import os
from datetime import datetime, timedelta

# ==========================================================
# 1. CONFIGURAÇÕES, ESTILO E NOME
# ==========================================================
APP_NAME = "AURA APOENA LOGISTICS"
st.set_page_config(page_title=APP_NAME, layout="wide")

st.markdown(f"""
<style>
    .stApp {{ background-color: #FFFFFF !important; }}
    [data-testid="stSidebar"] {{ background-color: #002D5E !important; }}
    h1, h2, h3, label, p {{ color: #002D5E !important; font-weight: 700; }}
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] label, [data-testid="stSidebar"] span {{ color: #FFFFFF !important; }}
    
    /* BOTÃO PADRÃO YARA */
    div.stButton > button, div[data-testid="stForm"] button {{
        background-color: #FFFFFF !important;
        border: 2px solid #002D5E !important;
        border-radius: 8px !important;
        height: 48px !important;
        width: 100% !important;
    }}
    div.stButton > button p, div[data-testid="stForm"] button p {{
        color: #002D5E !important; font-weight: 900;
    }}
    div.stButton > button:hover {{ background-color: #002D5E !important; }}
    div.stButton > button:hover p {{ color: #FFFFFF !important; }}
    
    /* TABELA DE OBSERVAÇÕES */
    .obs-header {{
        background-color: #E75945; color: white; text-align: center;
        padding: 8px; font-weight: bold; border: 1px solid #ddd;
    }}
    .obs-row {{ display: flex; border: 1px solid #ddd; }}
    .obs-day {{
        width: 150px; padding: 10px; background-color: #f9f9f9;
        border-right: 1px solid #ddd; font-weight: bold;
    }}
    .obs-content {{ flex-grow: 1; padding: 10px; color: #333; }}
</style>
""", unsafe_allow_html=True)

# ==========================================================
# 2. CONEXÃO GITHUB
# ==========================================================
@st.cache_data(ttl=5)
def carregar_dados():
    try:
        tk = st.secrets["GITHUB_TOKEN"]
        repo = Github(auth=Auth.Token(tk)).get_repo("yaramaia122-lgtm/logistica-aura")
        def ler(arq, cols):
            try:
                c = repo.get_contents(arq)
                return pd.read_csv(io.StringIO(c.decoded_content.decode())), c.sha
            except: return pd.DataFrame(columns=cols), None
        
        cols_v = ["Passageiro", "Motorista", "Data", "Trajeto", "Status", "Centro_Custo", 
                  "Hotel_V", "Comb_V", "Aereo_V", "Outro_V", "Total", "Voo", "Voo_Hora", "Hotel"]
        df_v, sh_v = ler("dados_logistica.csv", cols_v)
        df_u, sh_u = ler("usuarios.csv", ["Usuario", "Senha", "Perfil"])
        df_o, sh_o = ler("observacoes.csv", ["Data", "Observacao"])
        return df_v, sh_v, df_u, sh_u, df_o, sh_o, repo
    except: return None

banco = carregar_dados()
if not banco: st.stop()
df, sha_v, df_u, sha_u, df_o, sha_o, repo = banco

# ==========================================================
# 3. CONTROLE DE ACESSO
# ==========================================================
if 'logado' not in st.session_state: st.session_state['logado'] = False

if not st.session_state['logado']:
    st.markdown("<style>.stApp { background-color: #002D5E !important; }</style>", unsafe_allow_html=True)
    _, col_login, _ = st.columns([1, 1.2, 1])
    with col_login:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.image("https://raw.githubusercontent.com/yaramaia122-lgtm/logistica-aura/main/logo.png", width=250)
        st.markdown(f"<h2 style='color:white; text-align:center;'>{APP_NAME}</h2>", unsafe_allow_html=True)
        with st.form("login_app"):
            u = st.text_input("Usuário Corporativo")
            s = st.text_input("Senha", type="password")
            if st.form_submit_button("ENTRAR NO SISTEMA"):
                if not df_u[(df_u['Usuario']==u) & (df_u['Senha']==s)].empty:
                    st.session_state['logado'] = True; st.rerun()
                else: st.error("Acesso negado.")
else:
    # ==========================================================
    # 4. SISTEMA PRINCIPAL
    # ==========================================================
    with st.sidebar:
        st.image("https://raw.githubusercontent.com/yaramaia122-lgtm/logistica-aura/main/logo.png", width=180)
        st.write(f"Conectado: **{st.session_state.get('usuario_atual', 'Yara')}**")
        menu = st.radio("NAVEGAÇÃO", ["Agenda", "Programar Viagem", "Dashboard", "Administração"])
        if st.button("SAIR"):
            st.session_state['logado'] = False
            st.rerun()

    if menu == "Agenda":
        st.title("📅 Agenda de Logística")
        st.markdown('<div class="obs-header">Observações Semanais</div>', unsafe_allow_html=True)
        dias_nome = ["Segunda-Feira", "Terça-Feira", "Quarta-Feira", "Quinta-Feira", "Sexta-Feira", "Sábado", "Domingo"]
        hoje = datetime.now()
        ini_sem = hoje - timedelta(days=hoje.weekday())
        for i, nome in enumerate(dias_nome):
            dt_curr = (ini_sem + timedelta(days=i)).strftime('%d/%m/%Y')
            dt_label = (ini_sem + timedelta(days=i)).strftime('%d/%b').lower()
            txt_obs = ""
            if not df_o.empty and 'Data' in df_o.columns:
                match = df_o[df_o['Data'] == dt_curr]
                if not match.empty: txt_obs = match.iloc[0]['Observacao']
            st.markdown(f'<div class="obs-row"><div class="obs-day">{nome}<br><small>{dt_label}</small></div>'
                        f'<div class="obs-content">{txt_obs}</div></div>', unsafe_allow_html=True)
        st.markdown("---")
        f_data = st.date_input("Filtrar viagens do dia:", hoje.date())
        df_dia = df[(df['Data'] == f_data.strftime('%d/%m/%Y')) & (df['Status'] != "Cancelada")]
        if not df_dia.empty:
            for t in df_dia['Trajeto'].unique():
                st.subheader(f"📍 {t}")
                st.dataframe(df_dia[df_dia['Trajeto']==t][["Passageiro","Motorista","Centro_Custo","Voo","Voo_Hora","Hotel"]], use_container_width=True, hide_index=True)
        else: st.info("Nenhuma viagem ativa encontrada.")

    elif menu == "Programar Viagem":
        st.title("📝 Nova Programação")
        with st.form("f_programar"):
            c1, c2 = st.columns(2)
            px = c1.text_input("Passageiro").upper()
            mt = c1.selectbox("Motorista", ["Ilson", "Antonio", "Vagno", "Cido", "Outro"])
            tj = c1.selectbox("Trecho", ["Pontes e Lacerda x Cuiabá", "Cuiabá x Pontes e Lacerda", "Interno"])
            cc = c1.text_input("Centro de Custo")
            dt = c2.date_input("Data Viagem")
            hs = c2.text_input("Hora Saída")
            lh = c2.text_input("Hotel/Destino")
            st.markdown("### Valores e Voo")
            v1, v2, v3, v4 = st.columns(4)
            hv = v1.number_input("Hotel", 0.0); cv = v2.number_input("Combustível", 0.0)
            av = v3.number_input("Aéreo", 0.0); ov = v4.number_input("Outros", 0.0)
            vi = c1.text_input("Cia/Voo Nº"); vh = c2.text_input("Hora Voo")
            if st.form_submit_button("GRAVAR PROGRAMAÇÃO"):
                tot = hv + cv + av + ov
                nova = pd.DataFrame([{"Passageiro":px,"Motorista":mt,"Data":dt.strftime('%d/%m/%Y'),"Trajeto":tj,"Status":"Confirmada","Centro_Custo":cc,"Total":tot,"Hotel_V":hv,"Comb_V":cv,"Aereo_V":av,"Outro_V":ov,"Voo":vi,"Voo_Hora":vh,"Hotel":lh}])
                df_f = pd.concat([df, nova], ignore_index=True)
                repo.update_file("dados_logistica.csv", "Add", df_f.to_csv(index=False), sha_v); st.rerun()

    elif menu == "Dashboard":
        st.title("📊 Gestão Financeira")
        if not df.empty:
            df_at = df[df["Status"] != "Cancelada"]
            st.metric("Gasto Total Ativo", f"R$ {df_at['Total'].sum():,.2f}")
            if 'Centro_Custo' in df_at.columns:
                st.subheader("Custos por Centro de Custo")
                st.bar_chart(df_at.groupby('Centro_Custo')['Total'].sum())

    elif menu == "Administração":
        st.title("⚙️ Administração")
        t1, t2, t3 = st.tabs(["Viagens", "Usuários", "Observações"])
        with t1:
            ed_v = st.data_editor(df, use_container_width=True, hide_index=True)
            if st.button("Salvar Viagens"):
                repo.update_file("dados_logistica.csv", "EdV", ed_v.to_csv(index=False), sha_v); st.rerun()
        with t2:
            ed_u = st.data_editor(df_u, num_rows="dynamic", use_container_width=True)
            if st.button("Salvar Usuários"):
                repo.update_file("usuarios.csv", "EdU", ed_u.to_csv(index=False), sha_u); st.rerun()
        with t3:
            ed_o = st.data_editor(df_o, num_rows="dynamic", use_container_width=True)
            if st.button("Salvar Observações"):
                repo.update_file("observacoes.csv", "EdO", ed_o.to_csv(index=False), sha_o); st.rerun()
