import streamlit as st
import pandas as pd
from github import Github, Auth
import io
from datetime import datetime, timedelta

# --- 1. DESIGN PROFISSIONAL (SEM PRETO / AZUL CLARO) ---
st.set_page_config(page_title="AURA APOENA", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #F0F8FF; } /* Fundo azul claro bem suave */
    [data-testid="stSidebar"] { background-color: #002D5E !important; }
    
    /* ESTILO DOS INPUTS: AZUL CLARO (Sem Preto) */
    .stTextInput input, .stSelectbox div[data-baseweb="select"], .stNumberInput input {
        background-color: #E3F2FD !important;
        color: #002D5E !important;
        border: 1px solid #90CAF9 !important;
        border-radius: 8px !important;
    }
    
    /* LOGIN ORIGINAL (d11b80) */
    .lbl-login { color: #FFFFFF !important; font-weight: 600; }
    .login-input input { background-color: #FFFFFF !important; border-radius: 8px !important; }

    /* BOTÃO ACESSAR ORIGINAL */
    .stButton>button {
        background-color: #FFFFFF !important; color: #002D5E !important;
        font-weight: 800 !important; border-radius: 10px !important; height: 48px !important;
    }

    /* AGENDA CABEÇALHO VERMELHO */
    .header-red {
        background-color: #E75945; color: white; padding: 10px;
        text-align: center; font-weight: bold; border-radius: 10px 10px 0 0;
    }
    .row-white { display: flex; border: 1px solid #90CAF9; border-top: none; background: #E3F2FD; }
    .dia-box { width: 140px; padding: 10px; background: #BBDEFB; border-right: 1px solid #90CAF9; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- 2. BANCO DE DADOS ---
@st.cache_data(ttl=5)
def carregar_tudo():
    try:
        tk = st.secrets["GITHUB_TOKEN"]
        rp = Github(auth=Auth.Token(tk)).get_repo("yaramaia122-lgtm/logistica-aura")
        
        def ler_csv(arq, colunas):
            try:
                c = rp.get_contents(arq)
                d = pd.read_csv(io.StringIO(c.decoded_content.decode()))
                for cl in colunas:
                    if cl not in d.columns: d[cl] = ""
                return d, c.sha
            except: return pd.DataFrame(columns=colunas), None

        cols_viagens = ["Passageiro", "Motorista", "Data", "Hora_Saida", "Trajeto", "Status", 
                        "Centro_Custo", "Hotel_V", "Comb_V", "Aereo_V", "Outros_V", "Total", "Voo", "Voo_Hora", "Hotel"]
        
        dv, sv = ler_csv("dados_logistica.csv", cols_viagens)
        du, su = ler_csv("usuarios.csv", ["Usuario", "Senha"])
        do, so = ler_csv("observacoes.csv", ["Data", "Observacao"])
        return dv, sv, du, su, do, so, rp
    except: return None

banco = carregar_tudo()
if not banco: st.stop()
df, s_v, df_u, s_u, df_o, s_o, repo = banco

# --- 3. LOGIN (DESIGN d11b80 - PRESERVADO) ---
if 'logado' not in st.session_state: st.session_state['logado'] = False

if not st.session_state['logado']:
    st.markdown("<style>.stApp { background-color: #002D5E !important; }</style>", unsafe_allow_html=True)
    _, col_log, _ = st.columns([1, 1.2, 1])
    with col_log:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.image("https://raw.githubusercontent.com/yaramaia122-lgtm/logistica-aura/main/logo.png", width=280)
        st.markdown("<h2 style='color:white; text-align:center; letter-spacing:4px;'>LOGISTICAS</h2>", unsafe_allow_html=True)
        with st.form("login_aura"):
            st.markdown("<p class='lbl-login'>Usuário</p>", unsafe_allow_html=True)
            u = st.text_input("u", label_visibility="collapsed", key="u_login")
            st.markdown("<p class='lbl-login'>Senha</p>", unsafe_allow_html=True)
            p = st.text_input("p", type="password", label_visibility="collapsed", key="p_login")
            if st.form_submit_button("ACESSAR SISTEMA"):
                if not df_u[(df_u['Usuario'] == u) & (df_u['Senha'] == p)].empty:
                    st.session_state['logado'] = True; st.rerun()
                else: st.error("Acesso negado.")
else:
    # --- 4. SISTEMA PRINCIPAL ---
    with st.sidebar:
        st.image("https://raw.githubusercontent.com/yaramaia122-lgtm/logistica-aura/main/logo.png", width=160)
        aba = st.radio("MENU", ["📅 Agenda", "📝 Programar", "📊 Financeiro", "⚙️ Admin"])
        if st.button("SAIR"): st.session_state['logado'] = False; st.rerun()

    if aba == "📅 Agenda":
        st.title("📅 Agenda de Logística")
        st.markdown('<div class="header-red">Observações da Semana</div>', unsafe_allow_html=True)
        dias = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
        hj = datetime.now()
        seg = hj - timedelta(days=hj.weekday())
        for i, n in enumerate(dias):
            dt = (seg + timedelta(days=i)).strftime('%d/%m/%Y')
            lbl = (seg + timedelta(days=i)).strftime('%d/%m')
            obs = df_o[df_o['Data'] == dt]['Observacao'].values[0] if dt in df_o['Data'].values else ""
            st.markdown(f'<div class="row-white"><div class="dia-box">{n}<br><small>{lbl}</small></div>'
                        f'<div style="padding:10px; color:#002D5E;">{obs}</div></div>', unsafe_allow_html=True)
        
        st.markdown("---")
        dt_f = st.date_input("Filtrar viagens por dia:", hj.date())
        df_d = df[(df['Data'] == dt_f.strftime('%d/%m/%Y')) & (df['Status'] != "Cancelada")]
        if not df_d.empty:
            for tr in df_d['Trajeto'].unique():
                st.subheader(f"📍 {tr}")
                st.dataframe(df_d[df_d['Trajeto']==tr][["Passageiro", "Data", "Hora_Saida", "Voo", "Voo_Hora", "Hotel", "Motorista"]].style.set_properties(**{'background-color': '#E3F2FD', 'color': '#002D5E'}), use_container_width=True, hide_index=True)

    elif aba == "📝 Programar":
        st.title("📝 Nova Programação")
        with st.form("p_form"):
            c1, c2 = st.columns(2)
            px = c1.text_input("Passageiro").upper()
            mt = c1.selectbox("Motorista", ["Ilson", "Antonio", "Vagno", "Cido", "Outro"])
            tj = c1.selectbox("Trecho", ["P. Lacerda x Cuiabá", "Cuiabá x P. Lacerda", "Interno"])
            # LISTA SUSPENSA CENTRO DE CUSTO
            cc_lista = sorted(list(set(df["Centro_Custo"].unique()) | {"ADMINISTRATIVO", "MINA", "PLANTA", "GEOLOGIA", "SEGURANÇA"}))
            cc = c1.selectbox("Centro de Custo", cc_lista)
            
            dt, hs, lh = c2.date_input("Data"), c2.text_input("Hora Saída"), c2.text_input("Hotel/Destino")
            st.markdown("### 💰 Financeiro")
            f1, f2, f3, f4 = st.columns(4)
            vh, vc = f1.number_input("Hotel", 0.0), f2.number_input("Comb.", 0.0)
            va, vo = f3.number_input("Aéreo", 0.0), f4.number_input("Outros", 0.0)
            vn, vhr = c1.text_input("Cia/Voo Nº"), c2.text_input("Hora Voo")
            
            if st.form_submit_button("GRAVAR"):
                total = vh + vc + va + vo
                nova = pd.DataFrame([{"Passageiro":px,"Motorista":mt,"Data":dt.strftime('%d/%m/%Y'),"Hora_Saida":hs,"Trajeto":tj,"Status":"Confirmada","Centro_Custo":cc,"Hotel_V":vh,"Comb_V":vc,"Aereo_V":va,"Outros_V":vo,"Total":total,"Voo":vn,"Voo_Hora":vhr,"Hotel":lh}])
                df_f = pd.concat([df, nova], ignore_index=True)
                repo.update_file("dados_logistica.csv", "Add", df_f.to_csv(index=False), s_v); st.rerun()

    elif aba == "📊 Financeiro":
        st.title("📊 Gestão Financeira")
        if not df.empty:
            df_at = df[df["Status"] != "Cancelada"].copy()
            df_at["Total"] = pd.to_numeric(df_at["Total"], errors="coerce")
            st.metric("Gasto Total Ativo", f"R$ {df_at['Total'].sum():,.2f}")
            st.bar_chart(df_at.groupby("Centro_Custo")["Total"].sum())

    elif aba == "⚙️ Admin":
        st.title("⚙️ Administração")
        t1, t2, t3 = st.tabs(["Viagens", "Usuários", "Observações"])
        with t1:
            ed_v = st.data_editor(df, use_container_width=True, hide_index=True)
            if st.button("Salvar Viagens"):
                repo.update_file("dados_logistica.csv", "EdV", ed_v.to_csv(index=False), s_v); st.rerun()
        with t2:
            ed_u = st.data_editor(df_u, num_rows="dynamic", use_container_width=True)
            if st.button("Salvar Usuários"):
                repo.update_file("usuarios.csv", "EdU", ed_u.to_csv(index=False), s_u); st.rerun()
        with t3:
            ed_o = st.data_editor(df_o, num_rows="dynamic", use_container_width=True)
            if st.button("Salvar Obs"):
                repo.update_file("observacoes.csv", "EdO", ed_o.to_csv(index=False), s_o); st.rerun()
