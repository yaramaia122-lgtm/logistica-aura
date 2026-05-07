import streamlit as st
import pandas as pd
from github import Github, Auth
import io
from datetime import datetime, timedelta

# --- 1. DESIGN E IDENTIDADE VISUAL (SEM PRETO / AZUL CLARO) ---
st.set_page_config(page_title="AURA APOENA LOGISTICS", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #F0F8FF; }
    [data-testid="stSidebar"] { background-color: #002D5E !important; }
    label, p, span, h1, h2, h3 { color: #002D5E !important; font-weight: 700; }
    
    /* CAMPOS DE ENTRADA E DROPDOWNS: AZUL CLARO (SEM PRETO) */
    .stTextInput input, .stSelectbox div[data-baseweb="select"], 
    .stNumberInput input, .stDateInput input, .stTextArea textarea {
        background-color: #E3F2FD !important;
        color: #002D5E !important;
        border: 2px solid #90CAF9 !important;
        border-radius: 8px !important;
    }

    /* ESTILO DAS OPÇÕES SUSPENSAS */
    div[data-baseweb="popover"] ul { background-color: #FFFFFF !important; }
    div[role="option"] { color: #002D5E !important; background-color: #FFFFFF !important; }
    div[role="option"]:hover { background-color: #BBDEFB !important; }

    /* CABEÇALHOS DA AGENDA (CORES AURA) */
    .header-trecho {
        background-color: #002D5E; color: white !important; padding: 10px;
        text-align: center; font-weight: bold; border-radius: 5px 5px 0 0;
    }
    .header-obs {
        background-color: #FF7F50; color: white !important; padding: 10px;
        text-align: center; font-weight: bold; border-radius: 5px 5px 0 0;
    }

    /* BOTÕES */
    .stButton>button {
        background-color: #002D5E !important; color: white !important;
        border-radius: 10px !important; font-weight: bold !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. BANCO DE DADOS E CENTROS DE CUSTO ---
CC_LISTA = [
    "210301-Moagem", "210401-Planta", "210801-Lab", "210002-Manut Planta",
    "310101-RH/Adm", "320201-Gerência Geral", "311101-TI", "310801-Segurança",
    "121101-Geologia", "150101-Mina Ernesto", "320101-Suprimentos"
]

@st.cache_data(ttl=2)
def carregar_dados():
    try:
        tk = st.secrets["GITHUB_TOKEN"]
        rp = Github(auth=Auth.Token(tk)).get_repo("yaramaia122-lgtm/logistica-aura")
        
        def ler_ou_criar(nome, colunas):
            try:
                f = rp.get_contents(nome)
                df = pd.read_csv(io.StringIO(f.decoded_content.decode()))
                for col in colunas:
                    if col not in df.columns: df[col] = ""
                return df, f.sha
            except:
                df = pd.DataFrame(columns=colunas)
                return df, None

        dv, sv = ler_ou_criar("dados_logistica.csv", ["Passageiro","Motorista","Data","Hora_Saida","Trajeto","Status","Centro_Custo","Hotel_V","Comb_V","Aereo_V","Outros_V","Total","Voo","Voo_Hora","Hotel","Hospedagem"])
        du, su = ler_ou_criar("usuarios.csv", ["Usuario","Senha","Perfil","Status"])
        do, so = ler_ou_criar("observacoes.csv", ["Data","Observacao"])
        
        return dv, sv, du, su, do, so, rp
    except Exception as e:
        st.error(f"Erro de Conexão: {e}")
        return None

banco = carregar_dados()
if not banco: st.stop()
df_v, sha_v, df_u, sha_u, df_o, sha_o, repo = banco

# --- 3. LOGIN ---
if 'logado' not in st.session_state: st.session_state['logado'] = False

if not st.session_state['logado']:
    st.markdown("<style>.stApp { background-color: #002D5E !important; } label { color: white !important; }</style>", unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        st.image("https://raw.githubusercontent.com/yaramaia122-lgtm/logistica-aura/main/logo.png", width=250)
        st.markdown("<h2 style='color:white; text-align:center;'>LOGISTICAS</h2>", unsafe_allow_html=True)
        with st.form("login_form"):
            u = st.text_input("Usuário").strip()
            p = st.text_input("Senha", type="password")
            if st.form_submit_button("ACESSAR"):
                if not df_u[(df_u['Usuario'] == u) & (df_u['Senha'] == p)].empty:
                    st.session_state['logado'] = True
                    st.session_state['user'] = u
                    st.rerun()
                else: st.error("Usuário ou Senha Inválidos")
else:
    # --- 4. SISTEMA PRINCIPAL ---
    with st.sidebar:
        st.image("https://raw.githubusercontent.com/yaramaia122-lgtm/logistica-aura/main/logo.png", width=140)
        st.write(f"Conectado: **{st.session_state['user']}**")
        menu = st.radio("MENU", ["Agenda", "Programar", "Dashboard", "Administração"])
        if st.button("Sair"): st.session_state['logado'] = False; st.rerun()

    # --- ABA AGENDA (IDÊNTICA À IMAGEM) ---
    if menu == "Agenda":
        st.markdown('<div class="header-trecho">PONTES E LACERDA X CUIABÁ</div>', unsafe_allow_html=True)
        df_pl = df_v[df_v['Trajeto'] == "Pontes e Lacerda x Cuiabá"][["Passageiro", "Data", "Hora_Saida", "Voo", "Voo_Hora", "Hotel", "Motorista"]]
        st.dataframe(df_pl, use_container_width=True, hide_index=True)

        st.markdown('<br><div class="header-trecho">CUIABÁ X PONTES E LACERDA</div>', unsafe_allow_html=True)
        df_cp = df_v[df_v['Trajeto'] == "Cuiabá x Pontes e Lacerda"][["Passageiro", "Data", "Hora_Saida", "Voo", "Voo_Hora", "Hotel", "Hospedagem", "Motorista"]]
        st.dataframe(df_cp, use_container_width=True, hide_index=True)

        st.markdown('<br><div class="header-obs">OBSERVAÇÕES DA SEMANA (EDIÇÃO DIRETA)</div>', unsafe_allow_html=True)
        # Garantir que os dias da semana existem
        if df_o.empty:
            dias = [(datetime.now() - timedelta(days=datetime.now().weekday()) + timedelta(days=i)).strftime('%d/%m/%Y') for i in range(7)]
            df_o = pd.DataFrame({"Data": dias, "Observacao": [""]*7})
        
        obs_edit = st.data_editor(df_o, use_container_width=True, hide_index=True)
        if st.button("Salvar Observações"):
            repo.update_file("observacoes.csv", "Update Obs", obs_edit.to_csv(index=False), sha_o)
            st.success("Observações atualizadas!"); st.rerun()

    # --- ABA PROGRAMAR (INTEGRADA) ---
    elif menu == "Programar":
        with st.form("programar_form"):
            col1, col2 = st.columns(2)
            px = col1.text_input("Passageiro").upper()
            mt = col1.selectbox("Motorista", ["Ilson", "Antonio", "Vagno", "Cido", "Outro"])
            tr = col1.selectbox("Trecho", ["Pontes e Lacerda x Cuiabá", "Cuiabá x Pontes e Lacerda", "Interno"])
            cc = col1.selectbox("Centro de Custo", CC_LISTA)
            
            dt = col2.date_input("Data da Viagem")
            hs = col2.text_input("Hora de Saída")
            ht = col2.text_input("Hotel/Destino")
            
            st.markdown("### ✈️ Informações de Voo")
            v_n, v_h = col1.text_input("Nº do Voo"), col2.text_input("Horário do Voo")
            
            st.markdown("### 💰 Custos (Acesso Restrito)")
            c_h, c_c = col1.number_input("Custo Hotel", 0.0), col2.number_input("Custo Combustível", 0.0)
            c_a, c_o = col1.number_input("Custo Aéreo", 0.0), col2.number_input("Outros Custos", 0.0)
            
            if st.form_submit_button("AGENDAR VIAGEM"):
                total = c_h + c_c + c_a + c_o
                nova_v = pd.DataFrame([{"Passageiro":px,"Motorista":mt,"Data":dt.strftime('%d/%m/%Y'),"Hora_Saida":hs,"Trajeto":tr,"Status":"Confirmada","Centro_Custo":cc,"Hotel_V":c_h,"Comb_V":c_c,"Aereo_V":c_a,"Outros_V":c_o,"Total":total,"Voo":v_n,"Voo_Hora":v_h,"Hotel":ht}])
                df_final = pd.concat([df_v, nova_v], ignore_index=True)
                repo.update_file("dados_logistica.csv", "Nova Viagem", df_final.to_csv(index=False), sha_v)
                st.success("Viagem Integrada à Agenda!"); st.rerun()

    # --- ABA DASHBOARD (MÉTRICAS) ---
    elif menu == "Dashboard":
        df_v["Total"] = pd.to_numeric(df_v["Total"], errors="coerce").fillna(0)
        
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        kpi1.metric("Total de Viagens", len(df_v))
        kpi2.metric("Passageiros Únicos", df_v["Passageiro"].nunique())
        kpi3.metric("Investimento Total", f"R$ {df_v['Total'].sum():,.2f}")
        kpi4.metric("Motoristas Ativos", df_v["Motorista"].nunique())
        
        c_graf1, c_graf2 = st.columns(2)
        with c_graf1:
            st.write("**Gastos por Centro de Custo**")
            st.bar_chart(df_v.groupby("Centro_Custo")["Total"].sum())
        with c_graf2:
            st.write("**Viagens por Motorista**")
            st.bar_chart(df_v["Motorista"].value_counts())

    # --- ABA ADMINISTRAÇÃO ---
    elif menu == "Administração":
        tab1, tab2 = st.tabs(["💰 Controle de Custos", "👤 Usuários"])
        with tab1:
            st.write("Edite as informações financeiras e trajetos abaixo:")
            ed_financeiro = st.data_editor(df_v, use_container_width=True, hide_index=True)
            if st.button("Salvar Alterações Financeiras"):
                repo.update_file("dados_logistica.csv", "Edit Fin", ed_financeiro.to_csv(index=False), sha_v); st.rerun()
        
        with tab2:
            st.write("Gestão de Acessos")
            ed_u = st.data_editor(df_u, num_rows="dynamic", use_container_width=True)
            if st.button("Salvar Usuários"):
                repo.update_file("usuarios.csv", "Edit User", ed_u.to_csv(index=False), sha_u); st.rerun()
