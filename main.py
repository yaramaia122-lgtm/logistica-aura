import streamlit as st
import pandas as pd
from github import Github
import io
from datetime import datetime

# 1. PREVENÇÃO CONTRA TRADUTOR E IDIOMA
st.markdown('<html lang="pt-br">', unsafe_allow_html=True)

# 2. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Aura Apoena Logistics", layout="wide")

# 3. UI/UX DESIGNER - ESTILO PADRONIZADO E CORREÇÃO VISUAL
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    
    /* Barra Lateral Marinho */
    [data-testid="stSidebar"] {
        background-color: #002D5E !important;
        min-width: 280px;
    }
    
    /* DESTAQUE DA LOGO COM SOMBRA (RESOLVENDO ERRO DE CARREGAMENTO) */
    .logo-container {
        text-align: center;
        padding: 10px;
        filter: drop-shadow(0px 6px 12px rgba(0,0,0,0.5));
    }

    /* CAIXAS DE PREENCHIMENTO - AZUL CLARO E LETRAS PRETAS EM TODOS OS MÓDULOS */
    .stTextInput input, .stSelectbox div[data-baseweb="select"], .stDateInput input, .stNumberInput input {
        background-color: #F0F7FF !important; 
        border: 2px solid #002D5E !important;
        color: #000000 !important; /* Letras pretas */
        border-radius: 8px !important;
        height: 45px !important;
        font-weight: 500 !important;
    }
    
    /* Forçar cor preta no texto digitado e nos itens selecionados */
    input, div[data-baseweb="select"] span {
        color: #000000 !important;
    }

    /* Labels dos campos em Azul Marinho e Negrito */
    label, .stMarkdown p {
        color: #002D5E !important;
        font-weight: bold !important;
    }

    /* BOTÕES - AZUL CLARO COM TEXTO MARINHO */
    div.stButton > button {
        background-color: #E1E8F0 !important;
        color: #002D5E !important;
        border: 2px solid #002D5E !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        width: 100% !important;
        height: 50px !important;
        transition: all 0.3s !important;
    }
    
    div.stButton > button:hover {
        background-color: #002D5E !important;
        color: #E1E8F0 !important;
    }

    /* Tabelas sempre brancas */
    [data-testid="stDataFrame"], [data-testid="stTable"], .stDataEditor {
        background-color: #FFFFFF !important;
        border-radius: 10px !important;
    }
    
    h1, h2, h3 { color: #002D5E !important; font-weight: 700 !important; }
    
    /* Textos da Barra Lateral em Branco */
    [data-testid="stSidebar"] .stMarkdown p, [data-testid="stSidebar"] label {
        color: #FFFFFF !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 4. BACKEND (CONEXÃO GITHUB)
def carregar_sistema():
    colunas = ["Passageiro", "Motorista", "Data", "Trajeto", "Obs Itinerário", "Hotel (R$)", "Combustível (R$)", "Aéreo (R$)", "Outros (R$)", "Total (R$)"]
    try:
        g = Github(st.secrets["GITHUB_TOKEN"])
        repo = g.get_repo("yaramaia122-lgtm/logistica-aura")
        contents = repo.get_contents("dados_logistica.csv")
        df = pd.read_csv(io.StringIO(contents.decoded_content.decode()))
        for col in colunas:
            if col not in df.columns:
                df[col] = 0.0 if "R$" in col else ""
        return df, contents.sha, repo
    except:
        return pd.DataFrame(columns=colunas), None, None

df, sha, repo = carregar_sistema()

# 5. SIDEBAR / MENU
with st.sidebar:
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Tentativa de carregamento robusto da logo
    logo_url = "https://raw.githubusercontent.com/yaramaia122-lgtm/logistica-aura/main/Aura%20(Azul%20e%20Ocre)%20(1).png"
    
    # HTML robusto para a logo com sombra
    st.markdown(f'''
        <div class="logo-container">
            <img src="{logo_url}" width="220" onerror="this.src='https://github.com/yaramaia122-lgtm/logistica-aura/raw/main/Aura%20(Azul%20e%20Ocre)%20(1).png'">
        </div>
    ''', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    menu = st.radio("NAVEGAÇÃO:", ["📋 Agenda de Viagens", "📝 Programar Viagem", "💰 Financeiro"])

# 6. TELAS

if menu == "📋 Agenda de Viagens":
    st.title("📋 Agenda de Viagens")
    if not df.empty:
        # Exibe logística e a descrição de outros itinerários
        st.dataframe(df[["Passageiro", "Motorista", "Data", "Trajeto", "Obs Itinerário"]], use_container_width=True)
    else:
        st.info("Nenhum registro encontrado.")

elif menu == "📝 Programar Viagem":
    st.title("📝 Programar Viagem")
    with st.form("form_v", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            nome = st.text_input("Nome do Passageiro").upper()
            motorista = st.selectbox("Motorista Responsável", ["Ilson", "Antonio", "Outro"])
            v_hotel = st.number_input("Custo Hotel (R$)", min_value=0.0, step=1.0)
            v_aereo = st.number_input("Custo Passagem (R$)", min_value=0.0, step=1.0)
        with c2:
            data = st.date_input("Data Programada", datetime.now())
            trajeto = st.selectbox("Itinerário Principal", ["P. Lacerda x Cuiabá", "Interno", "Outro"])
            v_comb = st.number_input("Custo Combustível (R$)", min_value=0.0, step=1.0)
            v_outros = st.number_input("Outros Custos (R$)", min_value=0.0, step=1.0)
        
        obs_itinerario = st.text_input("Descrição de Outros / Observações do Trajeto")
        
        if st.form_submit_button("CONCLUIR CADASTRO"):
            if nome and repo:
                total_viagem = v_hotel + v_comb + v_aereo + v_outros
                nova_viagem = pd.DataFrame([[
                    nome, motorista, data.strftime('%d/%m/%Y'), trajeto, 
                    obs_itinerario, v_hotel, v_comb, v_aereo, v_outros, total_viagem
                ]], columns=df.columns)
                
                df_f = pd.concat([df, nova_viagem], ignore_index=True)
                csv_data = df_f.to_csv(index=False)
                if sha:
                    repo.update_file("dados_logistica.csv", "Update Logistica", csv_data, sha)
                else:
                    repo.create_file("dados_logistica.csv", "Início", csv_data)
                st.success(f"Viagem de {nome} salva com sucesso!")
                st.rerun()

elif menu == "💰 Financeiro":
    st.title("💰 Financeiro")
    st.markdown("### Controle de Custos Detalhado")
    # Edição completa de todos os campos
    df_editado = st.data_editor(df, num_rows="dynamic", use_container_width=True)
    
    if st.button("CONFIRMAR ATUALIZAÇÃO FINANCEIRA"):
        if repo:
            # Recalcula o total automático
            df_editado["Total (R$)"] = (df_editado["Hotel (R$)"] + 
                                       df_editado["Combustível (R$)"] + 
                                       df_editado["Aéreo (R$)"] + 
                                       df_editado["Outros (R$)"])
            csv_editado = df_editado.to_csv(index=False)
            repo.update_file("dados_logistica.csv", "Sync Financeiro", csv_editado, sha)
            st.success("Dados financeiros atualizados no servidor!")
            st.rerun()
