import streamlit as st
import pandas as pd
from github import Github, Auth
import io
from datetime import datetime, timedelta

# 1. ESTILO E CORES (AZUL MARINHO & BRANCO)
st.set_page_config(page_title="Aura Apoena Logistics", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #FFFFFF !important; }
    [data-testid="stSidebar"] { background-color: #002D5E !important; }
    h1, h2, h3, label, p { color: #002D5E !important; font-weight: 700; }
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] label, [data-testid="stSidebar"] span { color: #FFFFFF !important; }
    
    /* BOTÃO PADRÃO YARA */
    div.stButton > button, div[data-testid="stForm"] button {
        background-color: #FFFFFF !important;
        border: 2px solid #002D5E !important;
        border-radius: 8px !important;
        height: 48px !important;
        width: 100% !important;
    }
    div.stButton > button p, div[data-testid="stForm"] button p {
        color: #002D5E !important; font-weight: 900;
    }
    div.stButton > button:hover { background-color: #002D5E !important; }
    div.stButton > button:hover p { color: #FFFFFF !important; }
    
    .obs-box { background-color: #E75945; color: white; padding: 15px; border-radius: 8px; margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

# 2. ACESSO AO BANCO DE DADOS
@st.cache_data(ttl=5)
def carregar_bancos():
    try:
        tk = st.secrets["GITHUB_TOKEN"]
        repo = Github(auth=Auth.Token(tk)).get_repo("yaramaia122-lgtm/logistica-aura")
        
        def ler(arq, cols):
            try:
                c = repo.get_contents(arq)
                return pd.read_csv(io.StringIO(c.decoded_content.decode())), c.sha
            except: return pd.DataFrame(columns=cols), None

        df_v, sh_v = ler("dados_logistica.csv", ["Passageiro","Motorista","Data","Trajeto","Status","Hotel_V","Comb_V","Aereo_V","Outro_V","Total","Voo","Voo_Hora","Hotel"])
        df_u, sh_u = ler("usuarios.csv", ["Usuario","Senha","Perfil"])
        df_o, sh_o = ler("observacoes.csv", ["Data","Observacao"])
        return df_v, sh_v, df_u, sh_u, df_o, sh_o, repo
    except: return None

dados = carregar_bancos()
if not dados:
    st.error("Erro de conexão."); st.stop()
df, sha_v, df_u, sha_u, df_o, sha_o, repo = dados

# 3. LOGIN
if 'logado' not in st.session_state: st.session_state['logado'] = False

if not st.session_state['logado']:
    st.markdown("<style>.stApp { background-color: #002D5E !important; }</style>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1.2, 1])
    with c2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.image("https://raw.githubusercontent.com/yaramaia122-lgtm/logistica-aura/main/logo.png", width=220)
        with st.form("l"):
            st.markdown("<h3 style='color:white; text-align:center;'>LOGÍSTICA AURA</h3>", unsafe_allow_html=True)
            u = st.text_input("Usuário")
            s = st.text_input("Senha", type="password")
            if st.form_submit_button("ENTRAR NO SISTEMA"):
                if not df_u[(df_u['Usuario']==u) & (df_u['Senha']==s)].empty:
                    st.session_state['logado'] = True; st.rerun()
                else: st.error("Incorreto.")
else:
    # 4. MENU
    menu = st.sidebar.radio("MENU", ["Agenda", "Programar", "Dashboard", "Administração"])
    st.sidebar.image("https://raw.githubusercontent.com/yaramaia122-lgtm/logistica-aura/main/logo.png", width=150)
    if st.sidebar.button("SAIR"): st.session_state['logado']=False; st.rerun()

    # --- AGENDA ---
    if menu == "Agenda":
        st.title("📅 Agenda")
        dia = st.date_input("Escolha o dia:", datetime.now().date())
        dia_s = dia.strftime('%d/%m/%Y')
        
        # Observações
        obs = df_o[df_o['Data'] == dia_s]
        for o in obs['Observacao']:
            st.markdown(f"<div class='obs-box'><b>AVISO:</b> {o}</div>", unsafe_allow_html=True)

        if not df.empty:
            df_a = df[(df['Data'] == dia_s) & (df['Status'] != "Cancelada")]
            if not df_a.empty:
                for t in df_a['Trajeto'].unique():
                    st.subheader(f"📍 {t}")
                    st.dataframe(df_a[df_a['Trajeto']==t], use_container_width=True, hide_index=True)
            else: st.info("Sem viagens ativas.")

    # --- PROGRAMAR ---
    elif menu == "Programar":
        st.title("📝 Programar Viagem")
        with st.form("p"):
            c1, c2 = st.columns(2)
            px = c1.text_input("Passageiro").upper()
            mt = c1.selectbox("Motorista", ["Ilson", "Antonio", "Vagno", "Cido", "Outro"])
            tj = c1.selectbox("Trecho", ["Pontes e Lacerda x Cuiabá", "Cuiabá x Pontes e Lacerda", "Interno"])
            dt = c2.date_input("Data")
            hs = c2.text_input("Saída")
            lh = c2.text_input("Hotel/Destino")
            st.markdown("### Valores e Voo")
            v1, v2, v3, v4 = st.columns(4)
            h_v = v1.number_input("Hotel", 0.0); c_v = v2.number_input("Combustível", 0.0)
            a_v = v3.number_input("Aéreo", 0.0); o_v = v4.number_input("Outros", 0.0)
            v_i = c1.text_input("Cia/Voo"); v_h = c2.text_input("Hora Voo")
            
            if st.form_submit_button("SALVAR"):
                total = h_v + c_v + a_v + o_v
                nova = pd.DataFrame([{"Passageiro":px,"Motorista":mt,"Data":dt.strftime('%d/%m/%Y'),"Trajeto":tj,"Status":"Confirmada","Total":total,"Hotel_V":h_v,"Comb_V":c_v,"Aereo_V":a_v,"Outro_V":o_v,"Voo":v_i,"Voo_Hora":v_h,"Hotel":lh}])
                df_f = pd.concat([df, nova], ignore_index=True)
                repo.update_file("dados_logistica.csv", "Add", df_f.to_csv(index=False), sha_v)
                st.success("Salvo!");
