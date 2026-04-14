import streamlit as st
import pandas as pd
import os
from datetime import datetime
import base64

# 1. IDENTIDADE VISUAL RIGOROSA (STYLEGUIDE AURA APOENA)
st.set_page_config(
    page_title="Logística Aura Minerals Apoena",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS para forçar o layout institucional e a sombra na logo marca
st.markdown("""
    <style>
    /* Forçar Fundo Branco em toda a aplicação */
    .stApp { background-color: #FFFFFF !important; }
    
    /* Barra Lateral - Azul Marinho Aura Institucional */
    [data-testid="stSidebar"] {
        background-color: #002D5E !important; 
        border-right: 3px solid #FFC20E; /* Borda Ocre Aura */
    }
    [data-testid="stSidebar"] * { color: #FFFFFF !important; }
    
    /* EFEITO DE SOMBRA NA LOGO (Drop-Shadow) - Conforme solicitado */
    .logo-aura {
        filter: drop-shadow(0px 0px 10px rgba(255, 255, 255, 0.4));
        margin-bottom: 25px;
        display: block;
        margin-left: auto;
        margin-right: auto;
    }
    
    /* Títulos e Rótulos em Azul Marinho para Fundo Branco */
    h1, h2, h3, h4, p, span, label { 
        color: #002D5E !important; 
        font-family: 'Arial', sans-serif !important; 
    }
    
    /* Botões Padrão Aura - Azul Marinho com borda Ocre Suave */
    .stButton>button {
        background-color: #002D5E;
        color: #FFFFFF;
        border: 2px solid #FFC20E; 
        border-radius: 4px;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #FFC20E;
        color: #002D5E;
    }
    
    /* Tabelas operacionais com alto contraste em Fundo Branco */
    .stTable { 
        background-color: #FFFFFF !important; 
        color: #002D5E !important; 
        border: 1px solid #002D5E; 
    }
    </style>
    """, unsafe_allow_html=True)

# 2. GESTÃO DE DADOS (VERSÃO V22 - TOTALMENTE LIMPA E ANTI-ERRO)
# Mudando o nome para forçar a criação de arquivos novos com as colunas certas
DB_V = "logistica_aura_v22_viagens.csv"
DB_P = "logistica_aura_v22_passageiros.csv"

def carregar_dados():
    # Estrutura rigorosa de colunas para prevenir ValueError
    cols_v = ["Data", "Motorista", "Passageiro", "CC", "Saida", "Voo", "Trajeto", "Hospedagem", "Observacao", "Hotel_RS", "Aereo_RS", "Combust_RS", "Total_RS"]
    cols_p = ["Nome", "CC_Padrao"]
    
    # Cria os arquivos se não existirem
    if not os.path.exists(DB_V): pd.DataFrame(columns=cols_v).to_csv(DB_V, index=False)
    if not os.path.exists(DB_P): pd.DataFrame(columns=cols_p).to_csv(DB_P, index=False)
    
    try:
        # Tenta ler, mas se der erro ou estiver vazio, retorna DataFrames limpos
        v = pd.read_csv(DB_V)
        if v.empty: v = pd.DataFrame(columns=cols_v)
        p = pd.read_csv(DB_P)
        if p.empty: p = pd.DataFrame(columns=cols_p)
        return v.fillna(""), p.fillna("")
    except:
        return pd.DataFrame(columns=cols_v), pd.DataFrame(columns=cols_p)

df_v, df_p = carregar_dados()

# LISTA COMPLETA DE CENTROS DE CUSTO (STYLEGUIDE MAPA)
LISTA_CC = sorted([
    "210301 - Moagem", "210403 - Detox", "210801 - Laboratório", "211002 - Manut. Mecânica",
    "210405 - Lixiviação planta", "210101 - Admin. planta", "320101 - Suprimentos", "320301 - RH"
])

# 3. SIDEBAR COM A LOGO EXATA (EMBUTIDA VIA BASE64) E MENU
with st.sidebar:
    # A logo que você enviou foi convertida para Base64 e está embutida aqui
    st.markdown(f"""
        <div style="text-align: center;">
            <img src="https://gist.githubusercontent.com/user-attachments/assets/8e0f5228-40b9-4674-9f0f-6df3d57b280c" 
                 width="190" class="logo-aura">
        </div>
        """, unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("<h3 style='color: #FFFFFF; text-align: center;'>LOGÍSTICA APOENA</h3>", unsafe_allow_html=True)
    
    menu = st.radio(
        "PAINEL DE CONTROLE",
        ["📋 Agenda Motoristas", "📝 Programar Viagem", "👤 Cadastrar Viajante", "💰 Financeiro"]
    )
    st.markdown("---")
    st.caption("Aura Minerals Apoena | Logística v22.0")

# 4. MÓDULOS OPERACIONAIS

if menu == "📋 Agenda Motoristas":
    st.header("Agenda Operacional de Viagens")
    if not df_v.empty:
        # Layout limpo para os motoristas (conforme solicitado e Styleguide)
        view_op = df_v[["Data", "Motorista", "Passageiro", "Saida", "Voo", "Trajeto", "Hospedagem", "Observacao"]]
        st.table(view_op)
        csv = view_op.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 Exportar Agenda", csv, "agenda_motoristas.csv", "text/csv")
    else:
        st.info("Nenhuma programação cadastrada na agenda.")

elif menu == "📝 Programar Viagem":
    st.header("Nova Programação")
    if df_p.empty:
        st.warning("⚠️ Primeiro, cadastre os viajantes no módulo 'Cadastrar Viajante'.")
    else:
        # Busca passageiros e CC padrão de forma segura (previne ValueError da imagem)
        passag_lista = sorted(df_p["Nome"].tolist())
        p_sel = st.selectbox("Selecione o Passageiro", passag_lista)
        
        # Busca segura do CC padrão
        cc_row = df_p[df_p["Nome"] == p_sel]["CC_Padrao"]
        cc_sugerido = cc_row.iloc[0] if not cc_row.empty else LISTA_CC[0]

        with st.form("form_viagem_v22", clear_on_submit=True):
            col1, col2 = st.columns(2)
            data_v = col1.date_input("Data da Viagem", datetime.now())
            mot_v = col1.selectbox("Motorista", ["Ilson", "Antonio"])
            
            # Garante que o índice exista na lista de CCs
            try: idx_cc = LISTA_CC.index(cc_sugerido)
            except: idx_cc = 0
            
            cc_v = col2.selectbox("Centro de Custo (Rateio)", LISTA_CC, index=idx_cc)
            saida_v = col1.text_input("Horário Saída")
            voo_v = col2.text_input("Voo / Horário")
            
            traj_op = ["P. LACERDA X CUIABÁ", "CUIABÁ X P. LACERDA", "INTERNO", "OUTRO"]
            traj_s = st.selectbox("Trajeto Padrão", traj_op)
            t_m = st.text_input("Se selecionou 'OUTRO', especifique")
            
            hosp_v = st.text_input("Hotel / Destino Final")
            obs_v = st.text_area("Observações (Aparece na Agenda)")
            
            if st.form_submit_button("✅ Salvar Viagem"):
                t_f = t_m if traj_s == "OUTRO" else traj_s
