import streamlit as st
import pandas as pd
import os
import base64
from datetime import datetime

# 1. SETUP VISUAL (CORES INSTITUCIONAIS COM SOMBRA PRETA)
st.set_page_config(page_title="Logística Aura Minerals", layout="wide")

# Função para converter imagem local para Base64 (Garante que a logo carregue)
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

st.markdown("""
    <style>
    /* Forçar Fundo Branco para os dados */
    .stApp { background-color: #FFFFFF !important; }
    
    /* Barra Lateral - Azul Marinho Aura e Borda Limpa */
    [data-testid="stSidebar"] {
        background-color: #002D5E !important;
        border-right: 2px solid #002D5E !important; /* Ficou azul para sumir a linha */
    }
    [data-testid="stSidebar"] * { color: #FFFFFF !important; }
    
    /* SOMBRA NA LOGO (PRETA) - Solicitação do Usuário */
    .logo-aura {
        filter: drop-shadow(0px 0px 10px rgba(0, 0, 0, 0.8));
        display: block; margin: auto; padding-bottom: 20px;
    }
    
    /* FONTES GERAIS EM AZUL MARINHO */
    h1, h2, h3, h4, p, span, label, div, small { 
        color: #002D5E !important; 
    }
    
    /* Rótulos dos campos em Azul e Negrito */
    .stTextInput label, .stSelectbox label, .stDateInput label, .stTextArea label {
        color: #002D5E !important;
        font-weight: bold !important;
    }

    /* --- CAMPOS CINZAS COM LETRA PRETA (CONFORME PEDIDO) --- */
    input, select, textarea, div[data-baseweb="input"], div[data-baseweb="select"] > div {
        background-color: #E8E8E8 !important; 
        color: #000000 !important; 
    }
    input { color: #000000 !important; }
    textarea { color: #000000 !important; }
    div[role="listbox"] { color: #000000 !important; }

    /* BOTÃO AZUL AURA COM DETALHE OCRE */
    .stButton>button {
        background-color: #002D5E !important; 
        color: #FFFFFF !important;
        border: 2px solid #FFC20E !important; 
        border-radius: 5px;
        font-weight: bold; width: 100%;
        height: 3em;
    }
    .stButton>button:hover {
        background-color: #FFC20E; color: #002D5E !important;
    }
    
    /* Estilo das Tabelas e Financeiro */
    .stTable { background-color: white !important; border: 1px solid #002D5E; }
    [data-testid="stDataEditor"] { background-color: #E8E8E8 !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. BANCO DE DADOS (LÓGICA INALTERADA - SUA LÓGICA)
DB_V = "banco_viagens_oficial.csv"
DB_P = "banco_passageiros_oficial.csv"

def carregar_dados():
    cols_v = ["Data", "Motorista", "Passageiro", "CC", "Saida", "Voo", "Trajeto", "Hospedagem", "Observacao", "Valor"]
    if not os.path.exists(DB_V): pd.DataFrame(columns=cols_v).to_csv(DB_V, index=False)
    if not os.path.exists(DB_P): pd.DataFrame(columns=["Nome", "CC_Padrao"]).to_csv(DB_P, index=False)
    v = pd.read_csv(DB_V).fillna("")
    p = pd.read_csv(DB_P).fillna("")
    for c in cols_v:
        if c not in v.columns: v[c] = ""
    return v, p

df_v, df_p = carregar_dados()

# 3. BARRA LATERAL (LOGO LOCAL E TOTAIS)
with st.sidebar:
    # Tenta carregar a imagem localmente (Mais Seguro)
    img_path = "Aura (Azul e Ocre).png"
    if os.path.exists(img_path):
        img_base64 = get_base64_of_bin_file(img_path)
        st.markdown(f'<div style="text-align: center;"><img src="data:image/png;base64,{img_base64}" width="180" class="logo-aura"></div>', unsafe_allow_html=True)
    else:
        # Fallback de link externo (Caso o arquivo local falhe)
        st.markdown(f'<div style="text-align: center;"><img src="https://gist.githubusercontent.com/user-attachments/assets/8e0f5228-40b9-4674-9f0f-6df3d57b280c" width="180" class="logo-aura"></div>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown(f"👥 **Funcionários:** {len(df_p)}")
    st.markdown(f"🚛 **Total de Viagens:** {len(df_v)}")
    st.markdown("---")
    menu = st.radio("MÓDULOS OPERACIONAIS", ["📋 Agenda Motoristas", "📝 Programar Viagem", "👤 Cadastrar Viajante", "💰 Financeiro"])

# 4. MÓDULOS (SUA LÓGICA - INALTERADA)
if menu == "📋 Agenda Motoristas":
    st.header("📋 Agenda Operacional de Viagens")
    if not df_v.empty:
        # Exibição Profissional e Detalhada
        st.table(df_v[["Data", "Motorista", "Passageiro", "Saida", "Voo", "Trajeto", "Hospedagem", "Observacao"]])
    else:
        st.write("Nenhuma viagem programada.")

elif menu == "📝 Programar Viagem":
    st.header("📝 Detalhamento de Nova Viagem")
    if df_p.empty:
        st.error("⚠️ Cadastre um viajante primeiro.")
    else:
        with st.form("form_viagem_detalhado", clear_on_submit=True):
            col1, col2 = st.columns(2)
            p_sel = col1.selectbox("Passageiro*", sorted(df_p["Nome"].tolist()))
            mot_v = col1.selectbox("Motorista Designado*", ["Ilson", "Antonio"])
            data_v = col1.date_input("Data da Missão", datetime.now())
            
            saida_v = col2.text_input("Horário Saída*")
            voo_v = col2.text_input("Voo / Chegada")
            hosp_v = col2.text_input("Local Hospedagem")
            
            traj_v = st.selectbox("Trajeto Padrão", ["P. LACERDA X CUIABÁ", "CUIABÁ X P. LACERDA", "INTERNO", "OUTRO"])
            obs_v = st.text_area("Instruções Operacionais")
            
            if st.form_submit_button("✅ SALVAR PROGRAMAÇÃO"):
                if not saida_v:
                    st.error("❌ Digite o horário de saída.")
                else:
                    nova = pd.DataFrame([{"Data": data_v.strftime('%d/%m/%Y'), "Motorista": mot_v, "Passageiro": p_sel, "Saida": saida_v, "Voo": voo_v, "Trajeto": traj_v, "Hospedagem": hosp_v, "Observacao": obs_v}])
                    pd.concat([df_v, nova], ignore_index=True).to_csv(DB_V, index=False)
                    st.success("Salvo!")
                    st.rerun()

elif menu == "👤 Cadastrar Viajante":
    st.header("👤 Gestão de Funcionários")
    with st.form("cad_funcionario"):
        n = st.text_input("Nome Completo").upper()
        if st.form_submit_button("CADASTRAR"):
            if n:
                if n in df_p["Nome"].values:
                    st.warning("O funcionário já possui cadastro.")
                else:
                    pd.concat([df_p, pd.DataFrame([{"Nome": n, "CC_Padrao": "A Definir"}])], ignore_index=True).to_csv(DB_P, index=False)
                    st.success(f"✅ {n} cadastrado!")
                    st.rerun()
            else: st.error("Digite um nome.")
    st.write("---")
    st.subheader("Lista de Colaboradores")
    st.dataframe(df_p)

elif menu == "💰 Financeiro":
    st.header("💰 Auditoria Financeira")
    # Sua lógica de edição de dados intacta e funcional
    df_editado = st.data_editor(df_v, use_container_width=True, num_rows="dynamic")
    if st.button("💾 ATUALIZAR DADOS FINANCEIROS"):
        df_editado.to_csv(DB_V, index=False)
        st.success("✅ Financeiro Atualizado!")
