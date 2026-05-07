import streamlit as st
import pandas as pd
from github import Github, Auth
import io
import os
from datetime import datetime, timedelta

# 1. ESTILO AURA (DESIGN TELA D11B80 E AGENDA)
st.set_page_config(page_title="AURA APOENA", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #FFFFFF !important; }
    [data-testid="stSidebar"] { background-color: #002D5E !important; }
    h1, h2, h3, label, p { color: #002D5E !important; font-weight: 700; }
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] label { color: white !important; }
    
    /* INPUTS BRANCOS (TELA LOGIN D11B80) */
    div[data-testid="stForm"] .stTextInput input {
        background-color: #FFFFFF !important;
        color: #002D5E !important;
        border: 1px solid #002D5E !important;
    }
    
    /* BOTÃO ACESSAR SISTEMA */
    div.stButton > button {
        background-color: #FFFFFF !important; color: #002D5E !important;
        font-weight: 900 !important; border-radius: 8px !important;
        height: 45px !important; width: 100% !important;
    }

    /* AGENDA CABEÇALHO VERMELHO */
    .obs-header {
        background-color: #E75945; color: white; text-align: center;
        padding: 10px; font-weight: bold; border-radius: 5px 5px 0 0;
    }
    .obs-row { display: flex; border: 1px solid #ddd; border-top: none; }
    .obs-day { width: 140px; padding: 12px; background-color: #f8f9fa; border-right: 1px solid #ddd; font-weight: bold; }
    .obs-content { flex-grow: 1; padding: 12px; color: #333; min-height: 45px; }
</style>
""", unsafe_allow_html=True)

# 2. BANCO DE DADOS
@st.cache_data(ttl=5)
def carregar_dados():
    try:
        tk = st.secrets["GITHUB_TOKEN"]
        rp = Github(auth=Auth.Token(tk)).get_repo("yaramaia122-lgtm/logistica-aura")
        def ler(arq, cols):
            try:
                c = rp.get_contents(arq)
                txt = c.decoded_content.decode()
                df_l = pd.read_csv(io.StringIO(txt))
                for cl in cols:
                    if cl not in df_l.columns: df_l[cl] = ""
                return df_l, c.sha
            except: return pd.DataFrame(columns=cols), None

        cols_v = ["Passageiro", "Motorista", "Data", "Trajeto", "Status", "Centro_Custo", 
                  "Hotel_V", "Comb_V", "Aereo_V", "Outro_V", "Total", "Voo", "Voo_Hora", "Hotel", "Hora_Saida"]
        df_v, sh_v = ler("dados_logistica.csv", cols_v)
        df_u, sh_u = ler("usuarios.csv", ["Usuario", "Senha"])
        df_o, sh_o = ler("observacoes.csv", ["Data", "Observacao"])
        return df_v, sh_v, df_u, sh_u, df_o, sh_o, rp
    except: return None

res = carregar_dados()
if not res: st.stop()
df, s_v, df_u, s_u, df_o, s_o, repo = res

# 3. LOGIN (DESIGN TELA D11B80)
if 'logado' not in st.session_state: st.session_state['logado'] = False

if not st.session_state['logado']:
    st.markdown("<style>.stApp { background-color: #002D5E !important; } label { color: white !important; }</style>", unsafe_allow_html=True)
    _, col_log, _ = st.columns([1, 1.2, 1])
    with col_log:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.image("https://raw.githubusercontent.com/yaramaia122-lgtm/logistica-aura/main/logo.png", width=280)
        st.markdown("<h2 style='color:white; text-align:center; letter-spacing: 5px;'>LOGISTICAS</h2>", unsafe_allow_html=True)
        with st.form("login_form"):
            user = st.text_input("usuario")
            pswd = st.text_input("senha", type="password")
            if st.form_submit_button("ACESSAR SISTEMA"):
                if not df_u[(df_u['Usuario'] == user) & (df_u['Senha'] == pswd)].empty:
                    st.session_state['logado'] = True
                    st.rerun()
                else: st.error("Dados incorretos.")
else:
    # 4. SISTEMA PRINCIPAL
    with st.sidebar:
        st.image("https://raw.githubusercontent.com/yaramaia122-lgtm/logistica-aura/main/logo.png", width=180)
        aba = st.radio("MENU", ["Agenda", "Programar", "Dashboard", "Admin"])
        if st.button("SAIR"): 
            st.session_state['logado'] = False
            st.rerun()

    if aba == "Agenda":
        st.title("📅 Agenda Semanal")
        st.markdown('<div class="obs-header">Observações</div>', unsafe_allow_html=True)
        dias = ["Segunda-Feira", "Terça-Feira", "Quarta-Feira", "Quinta-Feira", "Sexta-Feira", "Sábado", "Domingo"]
        hj = datetime.now()
        ds = hj.weekday()
        seg = hj - timedelta(days=ds)
        for i, n in enumerate(dias):
            dc_obj = seg + timedelta(days=i)
            dt_c = dc_obj.strftime('%d/%m/%Y')
            lbl = dc_obj.strftime('%d/%m')
            txt = ""
            if dt_c in df_o['Data'].values:
                txt = df_o[df_o['Data'] == dt_c]['Observacao'].values[0]
            st.markdown(f'<div class="obs-row"><div class="obs-day">{n}<br><small>{lbl}</small></div>'
                        f'<div class="obs-content">{txt}</div></div>', unsafe_allow_html=True)
        st.markdown("---")
        fd = st.date_input("Filtrar data:", hj.date())
        ds_str = fd.strftime('%d/%m/%Y')
        df_d = df[(df['Data'] == ds_str) & (df['Status'] != "Cancelada")]
        if not df_d.empty:
            for tr in df_d['Trajeto'].unique():
                st.subheader(f"📍 {tr}")
                c_ag = ["Passageiro", "Data", "Hora_Saida", "Voo", "Voo_Hora", "Hotel", "Motorista"]
                st.dataframe(df_d[df_d['Trajeto']==tr][c_ag], use_container_width=True, hide_index=True)

    elif aba == "Programar":
        st.title("📝 Nova Programação")
        with st.form("p_form"):
            c1, c2 = st.columns(2)
            px = c1.text_input("Passageiro").upper()
            mt = c1.selectbox("Motorista", ["Ilson", "Antonio", "Vagno", "Cido", "Outro"])
            tj = c1.selectbox("Trecho", ["Pontes e Lacerda x Cuiabá", "Cuiabá x Pontes e Lacerda", "Interno"])
            cc = c1.text_input("Centro de Custo")
            dt = c2.date_input("Data")
            hs = c2.text_input("Hora Saída")
            lh = c2.text_input("Hotel/Destino")
            st.markdown("### Valores e Voo")
            v1, v2, v3, v4 = st.columns(4)
            vh = v1.number_input("Hotel", 0.0)
            vc = v2.number_input("Combust.", 0.0)
            va = v3.number_input("Aéreo", 0.0)
            vo = v4.number_input("Outros", 0.0)
            vn = c1.text_input("Cia/Voo")
            vhr = c2.text_input("Hora Voo")
            if st.form_submit_button("GRAVAR"):
                tot = vh + vc + va + vo
                nova = pd.DataFrame([{"Passageiro":px,"Motorista":mt,"Data":dt.strftime('%d/%m/%Y'),"Trajeto":tj,"Status":"Confirmada","Centro_Custo":cc,"Total":tot,"Hotel_V":vh,"Comb_V":vc,"Aereo_V":va,"Outro_V":vo,"Voo":vn,"Voo_Hora":vhr,"Hotel":lh,"Hora_Saida":hs}])
                df_f = pd.concat([df, nova], ignore_index=True)
                repo.update_file("dados_logistica.csv", "Add", df_f.to_csv(index=False), s_v)
                st.rerun()

    elif aba == "Dashboard":
        st.title("📊 Gestão Financeira")
        if not df.empty:
            df_at = df[df["Status"] != "Cancelada"].copy()
            v_tot = pd.to_numeric(df_at['Total']).sum()
            st.metric("Gasto Total Ativo", f"R$ {v_tot:,.2f}")
            st.subheader("Custos por Centro de Custo")
            df_cc = df_at.groupby("Centro_Custo")["Total"].sum()
            st.bar_chart(df_cc)

    elif aba == "Admin":
        st.title("⚙️ Administração")
        t1, t2, t3 = st.tabs(["Viagens", "Usuários", "Observações"])
        with t1:
            ed_v = st.data_editor(df, use_container_width=True, hide_index=True)
            if st.button("Salvar Viagens"):
                repo.update_file("dados_logistica.csv", "EdV", ed_v.to_csv(index=False), s_v)
                st.rerun()
        with t2:
            ed_u = st.data_editor(df_u, num_rows="dynamic", use_container_width=True)
            if st.button("Salvar Usuários"):
                repo.update_file("usuarios.csv", "EdU", ed_u.to_csv(index=False), s_u)
                st.rerun()
        with t3:
            ed_o = st.data_editor(df_o, num_rows="dynamic", use_container_width=True)
            if st.button("Salvar Observações"):
                repo.update_file("observacoes.csv", "EdO", ed_o.to_csv(index=False), s_o)
                st.rerun()
