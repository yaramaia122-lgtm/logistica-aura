import streamlit as st
import pandas as pd
from github import Github, Auth
import io
from datetime import datetime, timedelta

# 1. ESTILO E DESIGN MODERNO (TELA D11B80)
st.set_page_config(page_title="AURA APOENA", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #F4F7F9 !important; }
    [data-testid="stSidebar"] { background-color: #002D5E !important; }
    h1, h2, h3, label, p { color: #002D5E !important; font-weight: 700; }
    
    /* LOGIN - CAMPOS COM FUNDO BRANCO E TEXTO ESCURO */
    div[data-testid="stForm"] .stTextInput input {
        background-color: #FFFFFF !important;
        color: #002D5E !important;
        border-radius: 8px !important;
        border: 1px solid #E2E8F0 !important;
    }
    
    /* TÍTULO LOGISTICAS - BRANCO TOTAL */
    .titulo-login {
        color: #FFFFFF !important;
        text-align: center;
        letter-spacing: 5px;
        font-weight: 300;
        margin-top: -15px;
        margin-bottom: 25px;
    }

    /* BOTÃO ACESSAR - BRANCO COM FONTE AZUL */
    div.stButton > button {
        background-color: #FFFFFF !important;
        color: #002D5E !important;
        font-weight: 800 !important;
        border-radius: 10px !important;
        border: none !important;
        height: 48px !important;
    }
    
    /* AGENDA - CABEÇALHO VERMELHO */
    .header-obs {
        background-color: #E75945; color: white;
        padding: 10px; text-align: center; font-weight: bold;
        border-radius: 10px 10px 0 0;
    }
</style>
""", unsafe_allow_html=True)

# 2. CONEXÃO GITHUB
@st.cache_data(ttl=5)
def carregar_dados():
    try:
        tk = st.secrets["GITHUB_TOKEN"]
        rp = Github(auth=Auth.Token(tk)).get_repo("yaramaia122-lgtm/logistica-aura")
        def ler(arq, cols):
            try:
                c = rp.get_contents(arq)
                df_l = pd.read_csv(io.StringIO(c.decoded_content.decode()))
                for cl in cols:
                    if cl not in df_l.columns: df_l[cl] = ""
                return df_l, c.sha
            except: return pd.DataFrame(columns=cols), None

        cv = ["Passageiro", "Motorista", "Data", "Trajeto", "Status", "Centro_Custo", 
              "Hotel_V", "Comb_V", "Aereo_V", "Outro_V", "Total", "Voo", "Voo_Hora", "Hotel", "Hora_Saida"]
        df_v, sh_v = ler("dados_logistica.csv", cv)
        df_u, sh_u = ler("usuarios.csv", ["Usuario", "Senha"])
        df_o, sh_o = ler("observacoes.csv", ["Data", "Observacao"])
        return df_v, sh_v, df_u, sh_u, df_o, sh_o, rp
    except: return None

res = carregar_dados()
if not res: st.stop()
df, s_v, df_u, s_u, df_o, s_o, repo = res

# 3. TELA DE LOGIN (ESTILO IMAGEM D11B80)
if 'logado' not in st.session_state: st.session_state['logado'] = False

if not st.session_state['logado']:
    st.markdown("<style>.stApp { background-color: #002D5E !important; }</style>", unsafe_allow_html=True)
    _, col_l, _ = st.columns([1, 1, 1])
    with col_l:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.image("https://raw.githubusercontent.com/yaramaia122-lgtm/logistica-aura/main/logo.png", width=300)
        st.markdown("<h2 class='titulo-login'>LOGISTICAS</h2>", unsafe_allow_html=True)
        with st.form("login"):
            # IDENTIFICAÇÃO DENTRO DOS CAMPOS (PLACEHOLDER)
            u = st.text_input("Usuário", placeholder="Digite seu usuário", label_visibility="collapsed")
            p = st.text_input("Senha", type="password", placeholder="Digite sua senha", label_visibility="collapsed")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.form_submit_button("ACESSAR SISTEMA"):
                if not df_u[(df_u['Usuario'] == u) & (df_u['Senha'] == p)].empty:
                    st.session_state['logado'] = True; st.rerun()
                else: st.error("Usuário ou senha incorretos.")
else:
    # 4. SISTEMA PRINCIPAL
    with st.sidebar:
        st.image("https://raw.githubusercontent.com/yaramaia122-lgtm/logistica-aura/main/logo.png", width=180)
        menu = st.radio("MENU", ["Agenda", "Programar", "Financeiro", "Admin"])
        if st.button("SAIR"): st.session_state['logado'] = False; st.rerun()

    if menu == "Agenda":
        st.title("📅 Agenda Semanal")
        st.markdown('<div class="header-obs">Observações da Semana</div>', unsafe_allow_html=True)
        dias = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
        h = datetime.now()
        seg = h - timedelta(days=h.weekday())
        for i, n in enumerate(dias):
            dt_c = (seg + timedelta(days=i)).strftime('%d/%m/%Y')
            lbl = (seg + timedelta(days=i)).strftime('%d/%m')
            txt = df_o[df_o['Data'] == dt_c]['Observacao'].values[0] if dt_c in df_o['Data'].values else ""
            with st.container():
                c_dia, c_obs = st.columns([1, 4])
                c_dia.markdown(f"**{n}**\n{lbl}")
                c_obs.info(txt if txt else "Sem observações.")

        st.markdown("---")
        f_d = st.date_input("Ver viagens de:", h.date())
        df_d = df[(df['Data'] == f_d.strftime('%d/%m/%Y')) & (df['Status'] != "Cancelada")]
        if not df_d.empty:
            for tr in df_d['Trajeto'].unique():
                st.subheader(f"📍 {tr}")
                cols = ["Passageiro", "Data", "Hora_Saida", "Voo", "Voo_Hora", "Hotel", "Motorista"]
                st.dataframe(df_d[df_d['Trajeto']==tr][cols], use_container_width=True, hide_index=True)

    elif menu == "Programar":
        st.title("📝 Programação")
        with st.form("p"):
            c1, c2 = st.columns(2)
            px = c1.text_input("Passageiro").upper()
            mt = c1.selectbox("Motorista", ["Ilson", "Antonio", "Vagno", "Cido", "Outro"])
            tj = c1.selectbox("Trecho", ["P. Lacerda x Cuiabá", "Cuiabá x P. Lacerda", "Interno"])
            cc = c1.text_input("Centro de Custo")
            dt, hs, lh = c2.date_input("Data"), c2.text_input("Saída"), c2.text_input("Hotel")
            st.markdown("### Financeiro")
            v1, v2, v3, v4 = st.columns(4)
            vh, vc = v1.number_input("Hotel", 0.0), v2.number_input("Comb.", 0.0)
            va, vo = v3.number_input("Aéreo", 0.0), v4.number_input("Outros", 0.0)
            if st.form_submit_button("GRAVAR"):
                tot = vh + vc + va + vo
                nova = pd.DataFrame([{"Passageiro":px,"Motorista":mt,"Data":dt.strftime('%d/%m/%Y'),"Trajeto":tj,"Status":"Confirmada","Centro_Custo":cc,"Total":tot,"Hotel_V":vh,"Comb_V":vc,"Aereo_V":va,"Outro_V":vo,"Hotel":lh,"Hora_Saida":hs}])
                df_f = pd.concat([df, nova], ignore_index=True)
                repo.update_file("dados_logistica.csv", "Add", df_f.to_csv(index=False), s_v); st.rerun()

    elif menu == "Financeiro":
        st.title("📊 Dashboard Financeiro")
        if not df.empty:
            df_at = df[df["Status"] != "Cancelada"].copy()
            st.metric("Total Ativo", f"R$ {pd.to_numeric(df_at['Total']).sum():,.2f}")
            st.bar_chart(df_at.groupby("Centro_Custo")["Total"].sum())

    elif menu == "Admin":
        st.title("⚙️ Administração")
        t1, t2, t3 = st.tabs(["Viagens", "Usuários", "Obs"])
        with t1:
            ev = st.data_editor(df, use_container_width=True, hide_index=True)
            if st.button("Salvar Viagens"):
                repo.update_file("dados_logistica.csv", "EdV", ev.to_csv(index=False), s_v); st.rerun()
        with t2:
            eu = st.data_editor(df_u, num_rows="dynamic", use_container_width=True)
            if st.button("Salvar Usuários"):
                repo.update_file("usuarios.csv", "EdU", eu.to_csv(index=False), s_u); st.rerun()
        with t3:
            eo = st.data_editor(df_o, num_rows="dynamic", use_container_width=True)
            if st.button("Salvar Obs"):
                repo.update_file("observacoes.csv", "EdO", eo.to_csv(index=False), s_o); st.rerun()
