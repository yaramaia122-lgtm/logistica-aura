import streamlit as st
import pandas as pd
from github import Github, Auth
import io
from datetime import datetime, timedelta

# 1. CONFIGURAÇÕES VISUAIS (AZUL MARINHO E BRANCO)
st.set_page_config(page_title="Aura Apoena Logistics", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #FFFFFF !important; }
    [data-testid="stSidebar"] { background-color: #002D5E !important; }
    h1, h2, h3, label, p { color: #002D5E !important; font-weight: 700; }
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] label, [data-testid="stSidebar"] span { color: #FFFFFF !important; }
    
    /* BOTÃO PADRÃO YARA: TEXTO AZUL MARINHO NO BRANCO */
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

# 2. CONEXÃO COM O BANCO DE DADOS (GITHUB)
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

        # Definição das colunas com Centro de Custo e Financeiro
        df_v, sh_v = ler("dados_logistica.csv", ["Passageiro","Motorista","Data","Trajeto","Status","Centro_Custo","Hotel_V","Comb_V","Aereo_V","Outro_V","Total","Voo","Voo_Hora","Hotel"])
        df_u, sh_u = ler("usuarios.csv", ["Usuario","Senha","Perfil","Status"])
        df_o, sh_o = ler("observacoes.csv", ["Data","Observacao"])
        return df_v, sh_v, df_u, sh_u, df_o, sh_o, repo
    except: return None

banco = carregar_bancos()
if not banco:
    st.error("Erro de conexão com o GitHub."); st.stop()
df, sha_v, df_u, sha_u, df_o, sha_o, repo = banco

# 3. CONTROLE DE ACESSO
if 'logado' not in st.session_state: st.session_state['logado'] = False

if not st.session_state['logado']:
    st.markdown("<style>.stApp { background-color: #002D5E !important; }</style>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1.2, 1])
    with c2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.image("https://raw.githubusercontent.com/yaramaia122-lgtm/logistica-aura/main/logo.png", width=250)
        with st.form("l"):
            st.markdown("<h3 style='color:white; text-align:center;'>LOGÍSTICA AURA</h3>", unsafe_allow_html=True)
            u = st.text_input("Usuário")
            s = st.text_input("Senha", type="password")
            if st.form_submit_button("ENTRAR NO SISTEMA"):
                if not df_u[(df_u['Usuario']==u) & (df_u['Senha']==s)].empty:
                    st.session_state['logado'] = True; st.rerun()
                else: st.error("Acesso Negado.")
else:
    # 4. MENU LATERAL
    menu = st.sidebar.radio("MENU", ["Agenda", "Programar Viagem", "Dashboard", "Administração"])
    st.sidebar.image("https://raw.githubusercontent.com/yaramaia122-lgtm/logistica-aura/main/logo.png", width=180)
    if st.sidebar.button("SAIR DO SISTEMA"): st.session_state['logado']=False; st.rerun()

    # --- MÓDULO: AGENDA ---
    if menu == "Agenda":
        st.title("📅 Agenda de Viagens")
        dia = st.date_input("Filtrar por dia:", datetime.now().date())
        dia_s = dia.strftime('%d/%m/%Y')
        
        # Observações do Dia
        obs = df_o[df_o['Data'] == dia_s]
        for o in obs['Observacao']:
            st.markdown(f"<div class='obs-box'><b>AVISO IMPORTANTE:</b> {o}</div>", unsafe_allow_html=True)

        if not df.empty:
            df_a = df[(df['Data'] == dia_s) & (df['Status'] != "Cancelada")]
            if not df_a.empty:
                for t in df_a['Trajeto'].unique():
                    st.subheader(f"📍 {t}")
                    st.dataframe(df_a[df_a['Trajeto']==t][["Passageiro","Motorista","Centro_Custo","Voo","Voo_Hora","Hotel"]], use_container_width=True, hide_index=True)
            else: st.info("Nenhuma viagem ativa para hoje.")

    # --- MÓDULO: PROGRAMAR VIAGEM ---
    elif menu == "Programar Viagem":
        st.title("📝 Nova Programação")
        with st.form("p"):
            c1, c2 = st.columns(2)
            px = c1.text_input("Nome do Passageiro").upper()
            mt = c1.selectbox("Motorista", ["Ilson", "Antonio", "Vagno", "Cido", "Terceiro"])
            tj = c1.selectbox("Trecho", ["Pontes e Lacerda x Cuiabá", "Cuiabá x Pontes e Lacerda", "Interno"])
            cc = c1.text_input("Centro de Custo (Ex: Mina, Adm, Planta)")
            
            dt = c2.date_input("Data da Viagem")
            hs = c2.text_input("Hora de Saída")
            lh = c2.text_input("Hotel/Destino")
            
            st.markdown("### 💰 Gestão Financeira")
            v1, v2, v3, v4 = st.columns(4)
            h_v = v1.number_input("Hotel (R$)", 0.0); c_v = v2.number_input("Combustível (R$)", 0.0)
            a_v = v3.number_input("Aéreo (R$)", 0.0); o_v = v4.number_input("Outros (R$)", 0.0)
            
            st.markdown("### ✈️ Info Voo")
            f1, f2 = st.columns(2)
            v_i = f1.text_input("Cia/Voo Nº"); v_h = f2.text_input("Horário do Voo")
            
            if st.form_submit_button("SALVAR PROGRAMAÇÃO"):
                total = h_v + c_v + a_v + o_v
                nova = pd.DataFrame([{"Passageiro":px,"Motorista":mt,"Data":dt.strftime('%d/%m/%Y'),"Trajeto":tj,"Status":"Confirmada","Centro_Custo":cc,"Total":total,"Hotel_V":h_v,"Comb_V":c_v,"Aereo_V":a_v,"Outro_V":o_v,"Voo":v_i,"Voo_Hora":v_h,"Hotel":lh}])
                df_f = pd.concat([df, nova], ignore_index=True)
                repo.update_file("dados_logistica.csv", "Add", df_f.to_csv(index=False), sha_v)
                st.success("Viagem gravada com sucesso!"); st.rerun()

    # --- MÓDULO: DASHBOARD (GESTÃO FINANCEIRA) ---
    elif menu == "Dashboard":
        st.title("📊 Indicadores e Financeiro")
        if not df.empty:
            df_at = df[df["Status"] != "Cancelada"]
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Gasto Total Acumulado", f"R$ {df_at['Total'].sum():,.2f}")
            col2.metric("Viagens Ativas", len(df_at))
            col3.metric("Média por Viagem", f"R$ {df_at['Total'].mean():,.2f}")
            
            st.markdown("---")
            st.subheader("Custos por Centro de Custo")
            if 'Centro_Custo' in df_at.columns:
                custo_cc = df_at.groupby('Centro_Custo')['Total'].sum()
                st.bar_chart(custo_cc)
            
            st.subheader("Volume por Trecho")
            st.bar_chart(df_at['Trajeto'].value_counts())
        else: st.warning("Sem dados financeiros para exibir.")

    # --- MÓDULO: ADMINISTRAÇÃO (GESTÃO DE USUÁRIOS) ---
    elif menu == "Administração":
        st.title("⚙️ Painel Administrativo")
        t1, t2, t3 = st.tabs(["Base de Viagens", "Controle de Usuários", "Observações"])
        
        with t1:
            st.write("Edite ou cancele viagens diretamente na tabela:")
            ed_v = st.data_editor(df, use_container_width=True, hide_index=True)
            if st.button("SALVAR ALTERAÇÕES EM VIAGENS"):
                repo.update_file("dados_logistica.csv", "EdV", ed_v.to_csv(index=False), sha_v); st.rerun()
        
        with t2:
            st.write("Gestão de Acesso (Adicione ou Remova usuários):")
            ed_u = st.data_editor(df_u, num_rows="dynamic", use_container_width=True)
            if st.button("SALVAR ALTERAÇÕES EM USUÁRIOS"):
                repo.update_file("usuarios.csv", "EdU", ed_u.to_csv(index=False), sha_u); st.rerun()
        
        with t3:
            st.write("Gerencie os avisos que aparecem na Agenda:")
            ed_o = st.data_editor(df_o, num_rows="dynamic", use_container_width=True)
            if st.button("SALVAR OBSERVAÇÕES"):
                repo.update_file("observacoes.csv", "EdO", ed_o.to_csv(index=False), sha_o); st.rerun()
