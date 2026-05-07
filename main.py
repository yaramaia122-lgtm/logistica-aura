import streamlit as st
import pandas as pd
from github import Github, Auth
import io
from datetime import datetime, timedelta

# --- 1. DESIGN REFINADO (AZUL CLARO / SEM PRETO / DROPDOWNS CORRIGIDOS) ---
st.set_page_config(page_title="AURA APOENA", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #F0F8FF; }
    [data-testid="stSidebar"] { background-color: #002D5E !important; }

    /* RÓTULOS (LABELS) AZUL MARINHO */
    label { color: #002D5E !important; font-weight: 700 !important; }

    /* CAMPOS DE INPUT E LISTAS SUSPENSAS (AZUL CLARO) */
    .stTextInput input, .stSelectbox div[data-baseweb="select"], 
    .stNumberInput input, .stDateInput input {
        background-color: #E3F2FD !important;
        color: #002D5E !important;
        border: 2px solid #90CAF9 !important;
        border-radius: 8px !important;
    }
    
    /* FORÇAR FUNDO BRANCO/AZUL NAS LISTAS SUSPENSAS (DROPDOWNS) */
    div[data-baseweb="popover"] ul { background-color: #FFFFFF !important; }
    div[data-baseweb="popover"] li { color: #002D5E !important; background-color: #FFFFFF !important; }
    div[data-baseweb="popover"] li:hover { background-color: #BBDEFB !important; }

    /* LOGIN ORIGINAL */
    .lbl-login { color: #FFFFFF !important; font-weight: 600; }
    .stButton>button {
        background-color: #FFFFFF !important; color: #002D5E !important;
        font-weight: 800 !important; border-radius: 10px !important; height: 48px !important;
    }

    /* AGENDA ESTILO IMAGEM d08db3 */
    .agenda-header {
        background-color: #FF7F50 !important; color: white !important; 
        padding: 10px; text-align: center; font-weight: bold; border-radius: 10px 10px 0 0;
    }
    .agenda-row { display: flex; border: 1px solid #ddd; border-top: none; background-color: white; }
    .agenda-dia { width: 180px; padding: 12px; background: #F8F9FA; border-right: 1px solid #ddd; font-weight: bold; color: #002D5E; }
    .agenda-obs { flex-grow: 1; padding: 12px; color: #333; min-height: 45px; }
</style>
""", unsafe_allow_html=True)

# --- 2. BANCO DE DADOS ---
@st.cache_data(ttl=5)
def carregar_sistema():
    try:
        tk = st.secrets["GITHUB_TOKEN"]
        rp = Github(auth=Auth.Token(tk)).get_repo("yaramaia122-lgtm/logistica-aura")
        def ler(arq, cols):
            try:
                c = rp.get_contents(arq)
                d = pd.read_csv(io.StringIO(c.decoded_content.decode()))
                for cl in cols:
                    if cl not in d.columns: d[cl] = ""
                return d, c.sha
            except: return pd.DataFrame(columns=cols), None
        cv = ["Passageiro", "Motorista", "Data", "Hora_Saida", "Trajeto", "Status", "Centro_Custo", 
              "Hotel_V", "Comb_V", "Aereo_V", "Outros_V", "Total", "Voo", "Voo_Hora", "Hotel"]
        dv, sv = ler("dados_logistica.csv", cv)
        du, su = ler("usuarios.csv", ["Usuario", "Senha"])
        do, so = ler("observacoes.csv", ["Data", "Observacao"])
        return dv, sv, du, su, do, so, rp
    except: return None

res = carregar_sistema()
if not res: st.stop()
df, s_v, df_u, s_u, df_o, s_o, repo = res

# --- 3. LOGIN ---
if 'logado' not in st.session_state: st.session_state['logado'] = False

if not st.session_state['logado']:
    st.markdown("<style>.stApp { background-color: #002D5E !important; } label { color: white !important; }</style>", unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.image("https://raw.githubusercontent.com/yaramaia122-lgtm/logistica-aura/main/logo.png", width=280)
        st.markdown("<h2 style='color:white; text-align:center;'>LOGISTICAS</h2>", unsafe_allow_html=True)
        with st.form("login"):
            u = st.text_input("Usuário")
            p = st.text_input("Senha", type="password")
            if st.form_submit_button("ACESSAR SISTEMA"):
                if not df_u[(df_u['Usuario'] == u) & (df_u['Senha'] == p)].empty:
                    st.session_state['logado'] = True; st.rerun()
                else: st.error("Dados incorretos.")
else:
    # --- 4. SISTEMA ---
    with st.sidebar:
        st.image("https://raw.githubusercontent.com/yaramaia122-lgtm/logistica-aura/main/logo.png", width=160)
        menu = st.radio("NAVEGAÇÃO", ["Agenda", "Programar", "Financeiro", "Administração"])
        if st.button("SAIR"): st.session_state['logado'] = False; st.rerun()

    if menu == "Agenda":
        st.markdown('<div class="agenda-header">Observações da Semana</div>', unsafe_allow_html=True)
        dias = ["Segunda-Feira", "Terça-Feira", "Quarta-Feira", "Quinta-Feira", "Sexta-Feira", "Sábado", "Domingo"]
        ini = datetime.now() - timedelta(days=datetime.now().weekday())
        for i, n in enumerate(dias):
            dt = (ini + timedelta(days=i)).strftime('%d/%m/%Y')
            obs = df_o[df_o['Data'] == dt]['Observacao'].values[0] if dt in df_o['Data'].values else ""
            st.markdown(f'<div class="agenda-row"><div class="agenda-dia">{n}<br><small>{dt[:5]}</small></div>'
                        f'<div class="agenda-obs">{obs}</div></div>', unsafe_allow_html=True)
        
        st.info("💡 Para editar as observações acima, vá na aba 'Administração'.")
        st.markdown("---")
        f_dia = st.date_input("Viagens do Dia:")
        df_f = df[(df['Data'] == f_dia.strftime('%d/%m/%Y')) & (df['Status'] != "Cancelada")]
        if not df_f.empty:
            for tr in df_f['Trajeto'].unique():
                st.subheader(f"📍 {tr}")
                st.dataframe(df_f[df_f['Trajeto']==tr][["Passageiro", "Hora_Saida", "Voo", "Voo_Hora", "Hotel", "Motorista"]], use_container_width=True, hide_index=True)

    elif menu == "Programar":
        with st.form("p_form"):
            c1, c2 = st.columns(2)
            px = c1.text_input("Passageiro").upper()
            mt = c1.selectbox("Motorista", ["Ilson", "Antonio", "Vagno", "Cido", "Outro"])
            tj = c1.selectbox("Trecho", ["P. Lacerda x Cuiabá", "Cuiabá x P. Lacerda", "Interno"])
            cc_op = sorted(list(set(df["Centro_Custo"].unique()) | {"ADMINISTRATIVO", "MINA", "PLANTA"}))
            cc = c1.selectbox("Centro de Custo", cc_op)
            dt, hs, lh = c2.date_input("Data"), c2.text_input("Saída"), c2.text_input("Hotel/Destino")
            vn, vh = c1.text_input("Voo Nº"), c2.text_input("Hora Voo")
            if st.form_submit_button("GRAVAR"):
                nova = pd.DataFrame([{"Passageiro":px,"Motorista":mt,"Data":dt.strftime('%d/%m/%Y'),"Trajeto":tj,"Status":"Confirmada","Centro_Custo":cc,"Voo":vn,"Voo_Hora":vh,"Hotel":lh,"Hora_Saida":hs}])
                repo.update_file("dados_logistica.csv", "Add", pd.concat([df, nova]).to_csv(index=False), s_v); st.rerun()

    elif menu == "Financeiro":
        df["Total"] = pd.to_numeric(df["Total"], errors="coerce").fillna(0)
        st.metric("Total Ativo", f"R$ {df[df['Status']!='Cancelada']['Total'].sum():,.2f}")
        st.bar_chart(df.groupby("Centro_Custo")["Total"].sum())

    elif menu == "Administração":
        t1, t2, t3 = st.tabs(["Viagens", "Usuários", "Observações"])
        with t1:
            ev = st.data_editor(df, use_container_width=True, hide_index=True)
            if st.button("Salvar Viagens"): repo.update_file("dados_logistica.csv", "Ed", ev.to_csv(index=False), s_v); st.rerun()
        with t2:
            eu = st.data_editor(df_u, num_rows="dynamic", use_container_width=True)
            if st.button("Salvar Usuários"): repo.update_file("usuarios.csv", "Ed", eu.to_csv(index=False), s_u); st.rerun()
        with t3:
            eo = st.data_editor(df_o, num_rows="dynamic", use_container_width=True)
            if st.button("Salvar Obs"): repo.update_file("observacoes.csv", "Ed", eo.to_csv(index=False), s_o); st.rerun()
