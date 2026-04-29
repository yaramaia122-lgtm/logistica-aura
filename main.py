import streamlit as st
import pandas as pd
from github import Github
import io
from datetime import datetime

# 1. PREVENÇÃO CONTRA TRADUTOR
st.markdown('<html lang="pt-br">', unsafe_allow_html=True)

# 2. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Aura Apoena Logistics", layout="wide")

# 3. UI/UX - DESIGN PADRONIZADO E ESTÁVEL
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    
    /* Barra Lateral Marinho */
    [data-testid="stSidebar"] {
        background-color: #002D5E !important;
        min-width: 280px;
    }
    
    /* LOGO COM SOMBRA PROJETADA */
    .logo-container {
        text-align: center;
        padding: 20px 0px;
        filter: drop-shadow(0px 8px 12px rgba(0,0,0,0.7));
    }

    /* CAIXAS DE PREENCHIMENTO - AZUL CLARO / LETRAS PRETAS */
    .stTextInput input, .stSelectbox div[data-baseweb="select"], .stDateInput input, .stNumberInput input {
        background-color: #F0F7FF !important; 
        border: 2px solid #002D5E !important;
        color: #000000 !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
    }
    
    /* Labels em Azul Marinho */
    label, .stMarkdown p {
        color: #002D5E !important;
        font-weight: bold !important;
    }

    /* BOTÕES - AZUL CLARO / TEXTO MARINHO */
    div.stButton > button {
        background-color: #E1E8F0 !important;
        color: #002D5E !important;
        border: 2px solid #002D5E !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        height: 50px !important;
        width: 100% !important;
    }
    
    div.stButton > button:hover {
        background-color: #002D5E !important;
        color: #E1E8F0 !important;
    }

    /* Ajuste de cor de fontes na sidebar */
    [data-testid="stSidebar"] .stMarkdown p, [data-testid="stSidebar"] label {
        color: #FFFFFF !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 4. BACKEND (CONEXÃO GITHUB)
def carregar_dados():
    colunas = ["Passageiro", "Motorista", "Data", "Trajeto", "Obs Itinerário", "Hotel (R$)", "Combustível (R$)", "Aéreo (R$)", "Outros (R$)", "Total (R$)"]
    try:
        g = Github(st.secrets["GITHUB_TOKEN"])
        repo = g.get_repo("yaramaia122-lgtm/logistica-aura")
        contents = repo.get_contents("dados_logistica.csv")
        df = pd.read_csv(io.StringIO(contents.decoded_content.decode()))
        for c in colunas:
            if c not in df.columns: df[c] = 0.0 if "R$" in c else ""
        return df, contents.sha, repo
    except:
        return pd.DataFrame(columns=colunas), None, None

df, sha, repo = carregar_dados()

# 5. SIDEBAR
with st.sidebar:
    st.markdown("<br>", unsafe_allow_html=True)
    # Link da logo garantido
    logo = "https://raw.githubusercontent.com/yaramaia122-lgtm/logistica-aura/main/Aura%20(Azul%20e%20Ocre)%20(1).png"
    st.markdown(f'<div class="logo-container"><img src="{logo}" width="200"></div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    menu = st.radio("NAVEGAÇÃO:", ["📋 Agenda de Viagens", "📝 Programar Viagem", "💰 Financeiro"])

# 6. MÓDULOS

if menu == "📋 Agenda de Viagens":
    st.title("📋 Agenda de Viagens")
    if not df.empty:
        # Mostra apenas colunas de logística (sem valores)
        st.dataframe(df[["Passageiro", "Motorista", "Data", "Trajeto", "Obs Itinerário"]], use_container_width=True)
    else:
        st.info("Nenhuma viagem agendada.")

elif menu == "📝 Programar Viagem":
    st.title("📝 Programar Viagem")
    with st.form("registro_viagem", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            nome = st.text_input("Passageiro").upper()
            moto = st.selectbox("Motorista", ["Ilson", "Antonio", "Outro"])
            v_hotel = st.number_input("Hotel (R$)", min_value=0.0)
            v_aereo = st.number_input("Aéreo (R$)", min_value=0.0)
        with c2:
            data = st.date_input("Data", datetime.now())
            itinerarios = ["P. Lacerda x Cuiabá", "Interno", "Outro"]
            traj = st.selectbox("Itinerário Principal", itinerarios)
            v_comb = st.number_input("Combustível (R$)", min_value=0.0)
            v_outr = st.number_input("Outros (R$)", min_value=0.0)
        
        # Campo de descrição condicional
        desc_label = "Descreva o Itinerário (Obrigatório)" if traj == "Outro" else "Observações Adicionais"
        obs = st.text_input(desc_label)

        if st.form_submit_button("SALVAR LOGÍSTICA"):
            if nome and repo:
                total = v_hotel + v_comb + v_aereo + v_outr
                nova_linha = pd.DataFrame([[nome, moto, data.strftime('%d/%m/%Y'), traj, obs, v_hotel, v_comb, v_aereo, v_outr, total]], columns=df.columns)
                df_final = pd.concat([df, nova_linha], ignore_index=True)
                csv = df_final.to_csv(index=False)
                if sha: repo.update_file("dados_logistica.csv", "Sync", csv, sha)
                else: repo.create_file("dados_logistica.csv", "Init", csv)
                st.success("Registrado com sucesso!"); st.rerun()

elif menu == "💰 Financeiro":
    st.title("💰 Financeiro")
    st.write("Edite valores e custos diretamente na planilha:")
    df_edit = st.data_editor(df, num_rows="dynamic", use_container_width=True)
    
    if st.button("SINCRONIZAR FINANCEIRO"):
        if repo:
            # Recalcula o total automático antes de salvar
            df_edit["Total (R$)"] = df_edit["Hotel (R$)"] + df_edit["Combustível (R$)"] + df_edit["Aéreo (R$)"] + df_edit["Outros (R$)"]
            csv_edit = df_edit.to_csv(index=False)
            repo.update_file("dados_logistica.csv", "Edit", csv_edit, sha)
            st.success("Planilha atualizada!"); st.rerun()
