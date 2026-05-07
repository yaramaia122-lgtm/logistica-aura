import streamlit as st
import pandas as pd
from github import Github, Auth
import io
import os
from datetime import datetime, timedelta

# 1. CONFIGURAÇÕES E ESTILO
APP_NAME = "AURA APOENA LOGISTICS"
st.set_page_config(page_title=APP_NAME, layout="wide")

st.markdown(f"""
<style>
    .stApp {{ background-color: #FFFFFF !important; }}
    [data-testid="stSidebar"] {{ background-color: #002D5E !important; }}
    h1, h2, h3, label, p {{ color: #002D5E !important; font-weight: 700; }}
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] label, [data-testid="stSidebar"] span {{ color: #FFFFFF !important; }}
    div.stButton > button, div[data-testid="stForm"] button {{
        background-color: #FFFFFF !important; border: 2px solid #002D5E !important;
        border-radius: 8px !important; color: #002D5E !important;
        height: 45px !important; width: 100% !important; font-weight: 900 !important;
    }}
    .obs-header {{
        background-color: #E75945; color: white; text-align: center;
        padding: 10px; font-weight: bold; border: 1px solid #ddd; border-radius: 5px 5px 0 0;
    }}
    .obs-row {{ display: flex; border: 1px solid #ddd; border-top: none; }}
    .obs-day {{
        width: 140px; padding: 12px; background-color: #f8f9fa;
        border-right: 1px solid #ddd; font-weight: bold; font-size: 14px;
    }}
    .obs-content {{ flex-grow: 1; padding: 12px; color: #333; min-height: 45px; }}
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
                return pd.read_csv(io.StringIO(c.decoded_content.decode())), c.sha
            except: return pd.DataFrame(columns=cols), None

        cv = ["Passageiro", "Motorista", "Data", "Trajeto", "Status", "Centro_Custo", 
              "Hotel_V", "Comb_V", "Aereo_V", "Outro_V", "Total", "Voo", "Voo_Hora", "Hotel"]
        df_v, sh_v = ler("dados_logistica.csv", cv)
        df_u, sh_u = ler("usuarios.csv", ["Usuario", "Senha", "Perfil"])
        df_o, sh_o = ler("observacoes.csv", ["Data", "Observacao"])
        return df_v, sh_v, df_u, sh_u, df_o, sh_o, rp
    except: return None

banco = carregar_dados()
if not banco:
    st.error("Erro de conexão."); st.stop()
df, s_v, df_u, s_u, df_o, s_o, repo = banco

# 3. ACESSO
if 'logado' not in st.session_state: st.session_state['logado'] = False

if not st.session_state['logado']:
    st.markdown("<style>.stApp { background-color: #002D5E !important; }</style>", unsafe_allow_html=True)
    _, login_col, _ = st.columns([1, 1.2, 1])
    with login_col:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.image("https://raw.githubusercontent.com/yaramaia122-lgtm/logistica-aura/main/logo.png", width=250)
        st.markdown(f"<h2 style='color:white; text-align:center;'>{APP_NAME}</h2>", unsafe_allow_html=True)
        with st.form("f_l"):
            u = st.text_input("Usuário")
            p = st.text_input("Senha", type="password")
            if st.form_submit_button("ACESSAR SISTEMA"):
                if not df_u[(df_u['Usuario'] == u) & (df_u['Senha'] == p)].empty:
                    st.session_state['logado'] = True; st.rerun()
                else: st.error("Incorreto.")
else:
    # 4. SISTEMA
    with st.sidebar:
        st.image("https://raw.githubusercontent.com/yaramaia122-lgtm/logistica-aura/main/logo.png", width=180)
        aba = st.radio("MENU", ["📅 Agenda", "📝 Programar", "📊 Dashboard", "⚙️ Admin"])
        if st.button("SAIR"): st.session_state['logado'] = False; st.rerun()

    if aba == "📅 Agenda":
        st.title("📅 Agenda Semanal")
        st.markdown('<div class="obs-header">OBSERVAÇÕES DA SEMANA</div>', unsafe_allow_html=True)
        ds = ["Segunda-Feira", "Terça-Feira", "Quarta-Feira", "Quinta-Feira", "Sexta-Feira", "Sábado", "Domingo"]
        h = datetime.now()
        ini = h - timedelta(days=h.weekday())
        for i, n in enumerate(ds):
            dt = (ini + timedelta(days=i)).strftime('%d/%m/%Y')
            lb = (ini + timedelta(days=i)).strftime('%d/%m')
            tx = df_o[df_o['Data'] == dt]['Observacao'].values[0] if dt in df_o['Data'].values else ""
            st.markdown(f'<div class="obs-row"><div class="obs-day">{n}<br><small>{lb}</small></div>'
                        f'<div class="obs-content">{tx}</div></div>', unsafe_allow_html=True)
        st.markdown("---")
        f = st.date_input("Filtrar dia:", h.date())
        d = f.strftime('%d/%m/%Y')
        df_d = df[(df['Data'] == d) & (df['Status'] != "Cancelada")]
        if not df_d.empty:
            for tr in df_d['Trajeto'].unique():
                st.subheader(f"📍 {tr}")
                st.dataframe(df_d[df_d['Trajeto']==tr][["Passageiro","Motorista","Centro_Custo","Voo","Voo_Hora","Hotel"]], use_container_width=True, hide_index=True)

    elif aba == "📝 Programar":
        st.title("📝 Nova Viagem")
        with st.form("f_v"):
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
            val_h = v1.number_input("Hotel", 0.0)
            val_c = v2.number_input("Combustível", 0.0)
            val_a = v3.number_input("Aéreo", 0.0)
            val_o = v4.number_input("Outros", 0.0)
            v_n = c1.text_input("Voo Nº")
            v_h = c2.text_input("Hora Voo")
            if st.form_submit_button("GRAVAR"):
                tot = val_h + val_c + val_a + val_o
                nova = pd.DataFrame([{"Passageiro":px,"Motorista":mt,"Data":dt.strftime('%d/%m/%Y'),"Trajeto":tj,"Status":"Confirmada","Centro_Custo":cc,"Total":tot,"Hotel_V":val_h,"Comb_V":val_c,"Aereo_V":val_a,"Outro_V":val_o,"Voo":v_n,"Voo_Hora":v_h,"Hotel":lh}])
                df_f = pd.concat([df, nova], ignore_index=True)
                repo.update_file("dados_logistica.csv", "Add", df_f.to_csv(index=False), s_v); st.rerun()

    elif aba == "📊 Dashboard":
        st.title("📊 Gestão Financeira")
        if not df.empty:
            df_at = df[df["Status"] != "Cancelada"].copy()
            st.metric("Gasto Total Ativo", f"R$ {pd.to_numeric(df_at['Total']).sum():,.2f}")
            st.subheader("Custos por Centro de Custo")
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
            if st.button("Salvar Observações"):
                repo.update_file("observacoes.csv", "EdO", ed_o.to_csv(index=False), s_o); st.rerun()
