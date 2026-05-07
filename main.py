import streamlit as st
import pandas as pd
from github import Github, Auth
import io
from datetime import datetime, timedelta

# --- 1. DESIGN E IDENTIDADE VISUAL (SISTEMA AZUL CLARO / LOGIN MARINHO) ---
st.set_page_config(page_title="AURA APOENA LOGISTICS", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #F0F8FF; }
    [data-testid="stSidebar"] { background-color: #002D5E !important; }
    label, p, span, h1, h2, h3 { color: #002D5E !important; font-weight: 700; }
    
    /* INPUTS E DROPDOWNS: AZUL CLARO (SEM PRETO) */
    .stTextInput input, .stSelectbox div[data-baseweb="select"], 
    .stNumberInput input, .stDateInput input {
        background-color: #E3F2FD !important;
        color: #002D5E !important;
        border: 2px solid #90CAF9 !important;
        border-radius: 8px !important;
    }

    /* ESTILO DAS LISTAS SUSPENSAS - FORÇAR BRANCO/AZUL (SEM PRETO) */
    div[data-baseweb="popover"] ul { background-color: #FFFFFF !important; }
    div[role="option"] { color: #002D5E !important; background-color: #FFFFFF !important; }
    div[role="option"]:hover { background-color: #BBDEFB !important; }

    /* AGENDA (DESIGN d08db3) */
    .agenda-header {
        background-color: #FF7F50 !important; color: white !important; padding: 10px;
        text-align: center; font-weight: bold; border-radius: 10px 10px 0 0;
    }
    .trecho-header {
        background-color: #002D5E; color: white !important; padding: 10px;
        text-align: center; font-weight: bold; border-radius: 5px 5px 0 0;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. BANCO DE DADOS E CENTROS DE CUSTO ---
# Lista quebrada para evitar cortes de linha longa
CC_LISTA = ["210301-Moagem", "210401-Planta", "310101-RH/Adm", 
            "320201-Gerencia", "121101-Geologia", "150101-Mina"]

@st.cache_data(ttl=2)
def carregar_dados():
    try:
        tk = st.secrets["GITHUB_TOKEN"]
        rp = Github(auth=Auth.Token(tk)).get_repo("yaramaia122-lgtm/logistica-aura")
        def ler(arq, cols):
            try:
                f = rp.get_contents(arq)
                d = pd.read_csv(io.StringIO(f.decoded_content.decode()))
                for cl in cols:
                    if cl not in d.columns: d[cl] = ""
                return d, f.sha
            except: return pd.DataFrame(columns=cols), None
        
        dv, sv = ler("dados_logistica.csv", ["Passageiro","Motorista","Data","Hora_Saida","Trajeto","Status","Centro_Custo","Hotel_V","Comb_V","Aereo_V","Outros_V","Total","Voo","Voo_Hora","Hotel","Hospedagem"])
        du, su = ler("usuarios.csv", ["Usuario","Senha","Perfil"])
        do, so = ler("observacoes.csv", ["Data","Observacao"])
        return dv, sv, du, su, do, so, rp
    except: return None

banco = carregar_dados()
if not banco: st.stop()
df_v, sha_v, df_u, sha_u, df_o, sha_o, repo = banco

# --- 3. TELA DE LOGIN ORIGINAL (DESIGN d11b80) ---
if 'logado' not in st.session_state: st.session_state['logado'] = False

if not st.session_state['logado']:
    st.markdown("<style>.stApp { background-color: #002D5E !important; } label { color: white !important; }</style>", unsafe_allow_html=True)
    _, col_log, _ = st.columns([1, 1.2, 1])
    with col_log:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.image("https://raw.githubusercontent.com/yaramaia122-lgtm/logistica-aura/main/logo.png", width=280)
        st.markdown("<h2 style='color:white; text-align:center;'>LOGISTICAS</h2>", unsafe_allow_html=True)
        with st.form("login"):
            u = st.text_input("Usuário").strip()
            p = st.text_input("Senha", type="password")
            if st.form_submit_button("ACESSAR SISTEMA"):
                if not df_u[(df_u['Usuario'] == u) & (df_u['Senha'] == p)].empty:
                    st.session_state['logado'] = True; st.session_state['user'] = u; st.rerun()
                else: st.error("Acesso Negado")
else:
    # --- 4. SISTEMA PRINCIPAL ---
    with st.sidebar:
        st.image("https://raw.githubusercontent.com/yaramaia122-lgtm/logistica-aura/main/logo.png", width=140)
        menu = st.radio("MENU", ["Agenda", "Programar", "Dashboard", "Administração"])
        if st.button("Sair"): st.session_state['logado'] = False; st.rerun()

    if menu == "Agenda":
        # Observações Editáveis Diretas (Design d08db3)
        st.markdown('<div class="agenda-header">OBSERVAÇÕES DA SEMANA</div>', unsafe_allow_html=True)
        if df_o.empty:
            dias_v = [(datetime.now() - timedelta(days=datetime.now().weekday()) + timedelta(days=i)).strftime('%d/%m/%Y') for i in range(7)]
            df_o = pd.DataFrame({"Data": dias_v, "Observacao": [""]*7})
        
        obs_edit = st.data_editor(df_o, use_container_width=True, hide_index=True)
        if st.button("Salvar Observações"):
            repo.update_file("observacoes.csv", "Update", obs_edit.to_csv(index=False), sha_o); st.rerun()

        # Tabelas de Trajetos (Azul Claro)
        st.markdown('<br><div class="trecho-header">PONTES E LACERDA X CUIABÁ</div>', unsafe_allow_html=True)
        df_pl = df_v[df_v['Trajeto'] == "Pontes e Lacerda x Cuiabá"]
        st.dataframe(df_pl[["Passageiro", "Data", "Hora_Saida", "Voo", "Voo_Hora", "Hotel", "Motorista"]], use_container_width=True, hide_index=True)

        st.markdown('<br><div class="trecho-header">CUIABÁ X PONTES E LACERDA</div>', unsafe_allow_html=True)
        df_cp = df_v[df_v['Trajeto'] == "Cuiabá x Pontes e Lacerda"]
        st.dataframe(df_cp[["Passageiro", "Data", "Hora_Saida", "Voo", "Voo_Hora", "Hotel", "Hospedagem", "Motorista"]], use_container_width=True, hide_index=True)

    elif menu == "Programar":
        with st.form("prog"):
            c1, c2 = st.columns(2)
            px = c1.text_input("Passageiro").upper()
            mt = c1.selectbox("Motorista", ["Ilson", "Antonio", "Vagno", "Cido", "Outro"])
            trechos = ["Pontes e Lacerda x Cuiabá", "Cuiabá x Pontes e Lacerda", "Interno"]
            tj = c1.selectbox("Trecho", trechos)
            cc = c1.selectbox("Centro de Custo", CC_LISTA)
            dt, hs, ht = c2.date_input("Data"), c2.text_input("Hora Saída"), c2.text_input("Hotel/Destino")
            vn, vh = c1.text_input("Voo Nº"), c2.text_input("Hora Voo")
            
            st.markdown("### 💰 Financeiro (Privado)")
            f1, f2, f3, f4 = st.columns(4)
            c_h = f1.number_input("Hotel", 0.0)
            c_c = f2.number_input("Comb.", 0.0)
            c_a = f3.number_input("Aéreo", 0.0)
            c_o = f4.number_input("Outros", 0.0)
            
            if st.form_submit_button("AGENDAR"):
                total = c_h + c_c + c_a + c_o
                nova = pd.DataFrame([{"Passageiro":px,"Motorista":mt,"Data":dt.strftime('%d/%m/%Y'),"Hora_Saida":hs,"Trajeto":tj,"Status":"Confirmada","Centro_Custo":cc,"Hotel_V":c_h,"Comb_V":c_c,"Aereo_V":c_a,"Outros_V":c_o,"Total":total,"Voo":vn,"Voo_Hora":vh,"Hotel":ht}])
                repo.update_file("dados_logistica.csv", "Add", pd.concat([df_v, nova]).to_csv(index=False), sha_v); st.rerun()

    elif menu == "Dashboard":
        df_v["Total"] = pd.to_numeric(df_v["Total"], errors="coerce").fillna(0)
        st.metric("Gasto Total Ativo", f"R$ {df_v['Total'].sum():,.2f}")
        st.bar_chart(df_v.groupby("Centro_Custo")["Total"].sum())
        st.bar_chart(df_v["Motorista"].value_counts())

    elif menu == "Administração":
        tab1, tab2 = st.tabs(["💰 Custos", "👤 Usuários"])
        with tab1:
            ed_f = st.data_editor(df_v, use_container_width=True, hide_index=True)
            if st.button("Salvar Custos"): repo.update_file("dados_logistica.csv", "Edit", ed_f.to_csv(index=False), sha_v); st.rerun()
        with tab2:
            ed_u = st.data_editor(df_u, num_rows="dynamic", use_container_width=True)
            if st.button("Salvar Usuários"): repo.update_file("usuarios.csv", "Edit", ed_u.to_csv(index=False), sha_u); st.rerun()
