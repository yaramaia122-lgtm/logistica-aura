import streamlit as st
import pandas as pd
from github import Github, Auth
import io
from datetime import datetime, timedelta

# --- 1. DESIGN REFINADO (AZUL CLARO / SEM PRETO / RÓTULOS VISÍVEIS) ---
st.set_page_config(page_title="AURA APOENA", layout="wide")

st.markdown("""
<style>
    /* Fundo Geral */
    .stApp { background-color: #F0F8FF; }
    [data-testid="stSidebar"] { background-color: #002D5E !important; }

    /* RÓTULOS (LABELS) SEMPRE VISÍVEIS */
    label { 
        color: #002D5E !important; 
        font-weight: 700 !important; 
        font-size: 16px !important;
    }

    /* TELA DE LOGIN (Design d11b80) */
    .lbl-login { color: #FFFFFF !important; font-weight: 600; margin-bottom: 5px; }
    
    /* CAMPOS DE INPUT E LISTAS SUSPENSAS (AZUL CLARO - SEM PRETO) */
    .stTextInput input, .stSelectbox div[data-baseweb="select"], 
    .stNumberInput input, .stDateInput input {
        background-color: #E3F2FD !important;
        color: #002D5E !important;
        border: 2px solid #90CAF9 !important;
        border-radius: 8px !important;
    }
    
    /* CORREÇÃO DO TEXTO DENTRO DA LISTA SUSPENSA */
    div[data-baseweb="popover"] { background-color: #E3F2FD !important; }
    div[role="option"] { color: #002D5E !important; background-color: #E3F2FD !important; }

    /* BOTÃO ACESSAR ORIGINAL */
    .stButton>button {
        background-color: #FFFFFF !important; 
        color: #002D5E !important;
        font-weight: 800 !important; 
        border-radius: 10px !important; 
        height: 48px !important;
        border: none !important;
    }

    /* ESTILO DA AGENDA (CONFORME IMAGEM d08db3) */
    .agenda-header {
        background-color: #FF7F50 !important; /* Cor Salmão/Laranja */
        color: white !important; 
        padding: 10px; 
        text-align: center;
        font-weight: bold; 
        border: 1px solid #ddd;
        border-radius: 10px 10px 0 0;
    }
    .agenda-row { display: flex; border: 1px solid #ddd; border-top: none; background-color: white; }
    .agenda-dia { width: 180px; padding: 12px; background: #F8F9FA; border-right: 1px solid #ddd; font-weight: bold; color: #002D5E; }
    .agenda-obs { flex-grow: 1; padding: 12px; color: #333; min-height: 40px; }
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

# --- 3. LOGIN (DESIGN d11b80) ---
if 'logado' not in st.session_state: st.session_state['logado'] = False

if not st.session_state['logado']:
    st.markdown("<style>.stApp { background-color: #002D5E !important; } label { color: white !important; }</style>", unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.image("https://raw.githubusercontent.com/yaramaia122-lgtm/logistica-aura/main/logo.png", width=280)
        st.markdown("<h2 style='color:white; text-align:center; letter-spacing:4px;'>LOGISTICAS</h2>", unsafe_allow_html=True)
        with st.form("login"):
            user = st.text_input("Usuário")
            pswd = st.text_input("Senha", type="password")
            if st.form_submit_button("ACESSAR SISTEMA"):
                if not df_u[(df_u['Usuario'] == user) & (df_u['Senha'] == pswd)].empty:
                    st.session_state['logado'] = True; st.rerun()
                else: st.error("Dados incorretos.")
else:
    # --- 4. SISTEMA PRINCIPAL ---
    with st.sidebar:
        st.image("https://raw.githubusercontent.com/yaramaia122-lgtm/logistica-aura/main/logo.png", width=160)
        menu = st.radio("NAVEGAÇÃO", ["Agenda", "Programar", "Financeiro", "Administração"])
        if st.button("SAIR"): st.session_state['logado'] = False; st.rerun()

    if menu == "Agenda":
        st.markdown('<div class="agenda-header">Observações</div>', unsafe_allow_html=True)
        dias = ["Segunda-Feira", "Terça-Feira", "Quarta-Feira", "Quinta-Feira", "Sexta-Feira", "Sábado", "Domingo"]
        hj = datetime.now()
        ini = hj - timedelta(days=hj.weekday())
        for i, n in enumerate(dias):
            dt = (ini + timedelta(days=i)).strftime('%d/%m/%Y')
            lbl = (ini + timedelta(days=i)).strftime('%d/%m')
            obs = df_o[df_o['Data'] == dt]['Observacao'].values[0] if dt in df_o['Data'].values else ""
            st.markdown(f'<div class="agenda-row"><div class="agenda-dia">{n} ({lbl})</div>'
                        f'<div class="agenda-obs">{obs}</div></div>', unsafe_allow_html=True)
        
        st.markdown("---")
        dt_sel = st.date_input("Consultar viagens do dia:")
        df_dia = df[(df['Data'] == dt_sel.strftime('%d/%m/%Y')) & (df['Status'] != "Cancelada")]
        if not df_dia.empty:
            for tr in df_dia['Trajeto'].unique():
                st.subheader(f"📍 {tr}")
                st.dataframe(df_dia[df_dia['Trajeto']==tr][["Passageiro", "Data", "Hora_Saida", "Voo", "Voo_Hora", "Hotel", "Motorista"]], use_container_width=True, hide_index=True)

    elif menu == "Programar":
        with st.form("p_form"):
            c1, c2 = st.columns(2)
            px = c1.text_input("Passageiro").upper()
            mt = c1.selectbox("Motorista", ["Ilson", "Antonio", "Vagno", "Cido", "Outro"])
            tj = c1.selectbox("Trecho", ["P. Lacerda x Cuiabá", "Cuiabá x P. Lacerda", "Interno"])
            # CENTRO DE CUSTO - LISTA SUSPENSA
            cc_op = sorted(list(set(df["Centro_Custo"].unique()) | {"ADMINISTRATIVO", "MINA", "PLANTA"}))
            cc = c1.selectbox("Centro de Custo", cc_op)
            dt, hs, lh = c2.date_input("Data"), c2.text_input("Hora Saída"), c2.text_input("Hotel/Destino")
            st.markdown("### 💰 Financeiro")
            f1, f2, f3, f4 = st.columns(4)
            vh, vc = f1.number_input("Hotel", 0.0), f2.number_input("Comb.", 0.0)
            va, vo = f3.number_input("Aéreo", 0.0), f4.number_input("Outros", 0.0)
            vn, vhr = c1.text_input("Cia/Voo Nº"), c2.text_input("Hora Voo")
            if st.form_submit_button("GRAVAR"):
                nova = pd.DataFrame([{"Passageiro":px,"Motorista":mt,"Data":dt.strftime('%d/%m/%Y'),"Hora_Saida":hs,"Trajeto":tj,"Status":"Confirmada","Centro_Custo":cc,"Hotel_V":vh,"Comb_V":vc,"Aereo_V":va,"Outros_V":vo,"Total":vh+vc+va+vo,"Voo":vn,"Voo_Hora":vhr,"Hotel":lh}])
                repo.update_file("dados_logistica.csv", "Add", pd.concat([df, nova]).to_csv(index=False), s_v); st.rerun()

    elif menu == "Financeiro":
        df["Total"] = pd.to_numeric(df["Total"], errors="coerce").fillna(0)
        st.metric("Total Ativo", f"R$ {df[df['Status']!='Cancelada']['Total'].sum():,.2f}")
        st.bar_chart(df.groupby("Centro_Custo")["Total"].sum())

    elif menu == "Administração":
        t1, t2, t3 = st.tabs(["Viagens", "Usuários", "Observações"])
        with t1:
            edv = st.data_editor(df, use_container_width=True, hide_index=True)
            if st.button("Salvar Viagens"): repo.update_file("dados_logistica.csv", "Ed", edv.to_csv(index=False), s_v); st.rerun()
        with t2:
            edu = st.data_editor(df_u, num_rows="dynamic", use_container_width=True)
            if st.button("Salvar Usuários"): repo.update_file("usuarios.csv", "Ed", edu.to_csv(index=False), s_u); st.rerun()
        with t3:
            edo = st.data_editor(df_o, num_rows="dynamic", use_container_width=True)
            if st.button("Salvar Obs"): repo.update_file("observacoes.csv", "Ed", edo.to_csv(index=False), s_o); st.rerun()
