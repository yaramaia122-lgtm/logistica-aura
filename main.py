import streamlit as st
import pandas as pd
from github import Github, Auth
import io
from datetime import datetime, timedelta

# --- 1. DESIGN E IDENTIDADE (d11b80 + Agenda) ---
st.set_page_config(page_title="AURA APOENA", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #F4F7F9; }
    [data-testid="stSidebar"] { background-color: #002D5E !important; }
    h1, h2, h3, label { color: #002D5E !important; font-weight: 700; }
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] label { color: white !important; }

    /* Login d11b80: Campos Brancos com Rótulos Visíveis */
    .lbl-login { color: #FFFFFF !important; font-weight: 600; margin-bottom: 5px; }
    div[data-testid="stForm"] .stTextInput input {
        background-color: #FFFFFF !important; color: #002D5E !important;
        border-radius: 8px !important; border: 1px solid #E2E8F0 !important;
    }

    /* Botão Acessar */
    div.stButton > button {
        background-color: #FFFFFF !important; color: #002D5E !important;
        font-weight: 800 !important; border-radius: 10px !important;
        height: 48px !important; width: 100% !important; border: none !important;
    }

    /* Estilo Agenda */
    .header-obs {
        background-color: #E75945; color: white; padding: 12px;
        text-align: center; font-weight: bold; border-radius: 10px 10px 0 0;
    }
    .row-obs { display: flex; border: 1px solid #DDD; border-top: none; background: white; }
    .col-dia { width: 140px; padding: 10px; background: #F8F9FA; border-right: 1px solid #DDD; font-weight: bold; }
    .col-txt { flex-grow: 1; padding: 10px; color: #333; }
</style>
""", unsafe_allow_html=True)

# --- 2. BANCO DE DADOS (GITHUB) ---
@st.cache_data(ttl=5)
def carregar_dados():
    try:
        tk = st.secrets["GITHUB_TOKEN"]
        rp = Github(auth=Auth.Token(tk)).get_repo("yaramaia122-lgtm/logistica-aura")
        
        def ler(arq, cols):
            try:
                c = rp.get_contents(arq)
                d = pd.read_csv(io.StringIO(c.decoded_content.decode()))
                for cl in cols:
                    if cl not in d.columns: d[cl] = 0.0 if "Valor" in cl or cl == "Total" else ""
                return d, c.sha
            except: return pd.DataFrame(columns=cols), None

        cv = ["Passageiro", "Motorista", "Data", "Hora_Saida", "Trajeto", "Status", "Centro_Custo", 
              "Hotel_Valor", "Comb_Valor", "Aereo_Valor", "Outros_Valor", "Total", "Voo", "Voo_Hora", "Hotel"]
        
        dv, sv = ler("dados_logistica.csv", cv)
        du, su = ler("usuarios.csv", ["Usuario", "Senha"])
        do, so = ler("observacoes.csv", ["Data", "Observacao"])
        return dv, sv, du, su, do, so, rp
    except: return None

res = carregar_dados()
if not res: st.stop()
df, s_v, df_u, s_u, df_o, s_o, repo = res

# --- 3. LOGIN (DESIGN d11b80) ---
if 'logado' not in st.session_state: st.session_state['logado'] = False

if not st.session_state['logado']:
    st.markdown("<style>.stApp { background-color: #002D5E !important; }</style>", unsafe_allow_html=True)
    _, col_log, _ = st.columns([1, 1.2, 1])
    with col_log:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.image("https://raw.githubusercontent.com/yaramaia122-lgtm/logistica-aura/main/logo.png", width=280)
        st.markdown("<h2 style='color:white; text-align:center; letter-spacing:4px;'>LOGISTICAS</h2>", unsafe_allow_html=True)
        with st.form("login_form"):
            st.markdown("<p class='lbl-login'>Usuário</p>", unsafe_allow_html=True)
            u = st.text_input("u", label_visibility="collapsed")
            st.markdown("<p class='lbl-login'>Senha</p>", unsafe_allow_html=True)
            p = st.text_input("p", type="password", label_visibility="collapsed")
            if st.form_submit_button("ACESSAR SISTEMA"):
                if not df_u[(df_u['Usuario'] == u) & (df_u['Senha'] == p)].empty:
                    st.session_state['logado'] = True; st.rerun()
                else: st.error("Acesso negado.")
else:
    # --- 4. SISTEMA ---
    with st.sidebar:
        st.image("https://raw.githubusercontent.com/yaramaia122-lgtm/logistica-aura/main/logo.png", width=160)
        menu = st.radio("NAVEGAÇÃO", ["Agenda", "Programar", "Financeiro", "Administração"])
        if st.button("SAIR"): st.session_state['logado'] = False; st.rerun()

    if menu == "Agenda":
        st.title("📅 Agenda Semanal")
        st.markdown('<div class="header-obs">Observações da Semana</div>', unsafe_allow_html=True)
        dias = ["Segunda-Feira", "Terça-Feira", "Quarta-Feira", "Quinta-Feira", "Sexta-Feira", "Sábado", "Domingo"]
        h = datetime.now()
        ini = h - timedelta(days=h.weekday())
        for i, n in enumerate(dias):
            dt_c = (ini + timedelta(days=i)).strftime('%d/%m/%Y')
            lbl = (ini + timedelta(days=i)).strftime('%d/%m')
            tx = df_o[df_o['Data'] == dt_c]['Observacao'].values[0] if dt_c in df_o['Data'].values else ""
            st.markdown(f'<div class="row-obs"><div class="col-dia">{n}<br><small>{lbl}</small></div>'
                        f'<div class="col-txt">{tx}</div></div>', unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        f_d = st.date_input("Filtrar Viagens:", h.date())
        df_d = df[(df['Data'] == f_d.strftime('%d/%m/%Y')) & (df['Status'] != "Cancelada")]
        if not df_d.empty:
            for tr in df_d['Trajeto'].unique():
                st.subheader(f"📍 {tr}")
                df_v = df_d[df_d['Trajeto']==tr][["Passageiro", "Data", "Hora_Saida", "Voo", "Voo_Hora", "Hotel", "Motorista"]]
                st.dataframe(df_v, use_container_width=True, hide_index=True)

    elif menu == "Programar":
        st.title("📝 Programar Viagem")
        with st.form("p_form"):
            c1, c2 = st.columns(2)
            px, mt = c1.text_input("Passageiro").upper(), c1.selectbox("Motorista", ["Ilson", "Antonio", "Vagno", "Cido", "Outro"])
            tj, cc = c1.selectbox("Trecho", ["P. Lacerda x Cuiabá", "Cuiabá x P. Lacerda", "Interno"]), c1.text_input("Centro de Custo")
            dt, hs, lh = c2.date_input("Data"), c2.text_input("Hora Saída"), c2.text_input("Hotel/Destino")
            st.markdown("### 💰 Custos e Voo")
            f1, f2, f3, f4 = st.columns(4)
            vh, vc = f1.number_input("Hotel", 0.0), f2.number_input("Combust.", 0.0)
            va, vo = f3.number_input("Aéreo", 0.0), f4.number_input("Outros", 0.0)
            vn, vhr = c1.text_input("Cia/Voo Nº"), c2.text_input("Hora do Voo")
            if st.form_submit_button("SALVAR"):
                total = vh + vc + va + vo
                nova = pd.DataFrame([{"Passageiro":px,"Motorista":mt,"Data":dt.strftime('%d/%m/%Y'),"Hora_Saida":hs,"Trajeto":tj,"Status":"Confirmada","Centro_Custo":cc,"Hotel_Valor":vh,"Comb_Valor":vc,"Aereo_Valor":va,"Outros_Valor":vo,"Total":total,"Voo":vn,"Voo_Hora":vhr,"Hotel":lh}])
                df_f = pd.concat([df, nova], ignore_index=True)
                repo.update_file("dados_logistica.csv", "Add", df_f.to_csv(index=False), s_v); st.rerun()

    elif menu == "Financeiro":
        st.title("📊 Dashboard")
        if not df.empty:
            df_at = df[df["Status"] != "Cancelada"].copy()
            df_at["Total"] = pd.to_numeric(df_at["Total"], errors="coerce")
            st.metric("Gasto Total Ativo", f"R$ {df_at['Total'].sum():,.2f}")
            st.bar_chart(df_at.groupby("Centro_Custo")["Total"].sum())

    elif menu == "Administração":
        st.title("⚙️ Administração")
        t1, t2, t3 = st.tabs(["Viagens", "Usuários", "Observações"])
        with t1:
            edv = st.data_editor(df, use_container_width=True, hide_index=True)
            if st.button("Salvar Viagens"):
                repo.update_file("dados_logistica.csv", "EdV", edv.to_csv(index=False), s_v); st.rerun()
        with t2:
            edu = st.data_editor(df_u, num_rows="dynamic", use_container_width=True)
            if st.button("Salvar Usuários"):
                repo.update_file("usuarios.csv", "EdU", edu.to_csv(index=False), s_u); st.rerun()
        with t3:
            edo = st.data_editor(df_o, num_rows="dynamic", use_container_width=True)
            if st.button("Salvar Observações"):
                repo.update_file("observacoes.csv", "EdO", edo.to_csv(index=False), s_o); st.rerun()
