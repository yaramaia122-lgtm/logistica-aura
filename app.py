import streamlit as st
import pandas as pd
import os
from datetime import datetime
import base64

# 1. SETUP VISUAL RIGOROSO (STYLEGUIDE AURA MINERALS)
st.set_page_config(
    page_title="Aura Minerals - Logística Apoena",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização CSS para forçar o Fundo Branco e Cores Institucionais
st.markdown("""
    <style>
    /* Fundo Global */
    .stApp { background-color: #FFFFFF !important; }
    
    /* Barra Lateral (Menu) */
    [data-testid="stSidebar"] {
        background-color: #002D5E !important; /* Azul Aura */
    }
    [data-testid="stSidebar"] * { color: #FFFFFF !important; }
    
    /* Títulos e Textos */
    h1, h2, h3, h4, p, span, label { 
        color: #002D5E !important; 
        font-family: 'Benton Sans', sans-serif !important; 
    }
    
    /* Botões Padrão */
    .stButton>button {
        background-color: #002D5E;
        color: #FFFFFF;
        border: 2px solid #FFC20E; /* Amarelo/Ocre */
        border-radius: 4px;
        font-weight: bold;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #FFC20E;
        color: #002D5E;
    }
    
    /* Botão de Download (Destaque Amarelo) */
    .stDownloadButton>button {
        background-color: #FFC20E !important;
        color: #002D5E !important;
        font-weight: 800 !important;
    }
    
    /* Tabelas */
    .stTable, [data-testid="stDataFrame"] {
        background-color: #FFFFFF;
        border: 1px solid #002D5E;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. INTELIGÊNCIA DE DADOS (BANCO DE DADOS LOCAL)
DB_VIAGENS = "logistica_viagens_v6.csv"
DB_PASSAGEIROS = "cadastro_passageiros_v6.csv"

# Definição rigorosa de colunas para evitar o erro de index
COLS_VIAGENS = [
    "Data", "Motorista", "Passageiro", "CC", "Saida", 
    "Voo", "Trajeto", "Hospedagem", "Observacao", 
    "Hotel_RS", "Aereo_RS", "Combustivel_RS", "Total_RS"
]
COLS_PASSAGEIROS = ["Nome", "CC_Padrao"]

def gerenciar_banco():
    """Garante que os arquivos existam e tenham as colunas certas"""
    if not os.path.exists(DB_VIAGENS):
        pd.DataFrame(columns=COLS_VIAGENS).to_csv(DB_VIAGENS, index=False)
    if not os.path.exists(DB_PASSAGEIROS):
        pd.DataFrame(columns=COLS_PASSAGEIROS).to_csv(DB_PASSAGEIROS, index=False)

gerenciar_banco()

def load_data(file): return pd.read_csv(file).fillna("")
def save_data(df, file): df.to_csv(file, index=False)

# 3. COMPONENTES DE INTERFACE E RATEIO
LISTA_CC = sorted([
    "210301 - Moagem", "210403 - Detox", "210801 - Laboratório", "211002 - Manut. Mecânica",
    "210405 - Lixiviação planta", "210101 - Admin. planta", "211001 - Manut. Elétrica",
    "320101 - Suprimentos", "320301 - RH", "121101 - Geologia Ernesto", "121001 - Planejamento Mina",
    "310501 - Meio Ambiente", "310503 - Segurança Trabalho", "310502 - Saúde", "151101 - Geologia Nosde"
])

# 4. SIDEBAR COM IDENTIDADE VISUAL E LOGO NOVA
# Usando a logo estável inserida na nuvem via método Base64
with st.sidebar:
    # LINK ESTÁVEL PARA A LOGO DA AURA QUE ME ENVIASTE
    st.image("https://gist.githubusercontent.com/user-attachments/assets/8e0f5228-40b9-4674-9f0f-6df3d57b280c", width=200)
    st.markdown("---")
    st.markdown("### PAINEL OPERACIONAL")
    opcao = st.radio(
        "Selecione o Módulo:",
        ["📅 Agenda Motoristas", "📝 Programar Viagem", "👤 Cadastrar Viajante", "💰 Financeiro"]
    )
    st.markdown("---")
    st.caption("Aura Minerals Apoena - Logística v6.0")

# 5. MÓDULOS
if opcao == "📅 Agenda Motoristas":
    st.header("Agenda de Viagens Operacionais")
    df = load_data(DB_VIAGENS)
    if df.empty:
        st.info("Nenhuma viagem programada.")
    else:
        # Layout focado no Motorista (conforme solicitado e Styleguide)
        view_op = df[["Data", "Motorista", "Passageiro", "Saida", "Voo", "Trajeto", "Hospedagem", "Observacao"]]
        st.table(view_op)
        
        csv = view_op.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 Exportar Agenda para Motoristas", csv, "agenda_aura.csv", "text/csv")

elif opcao == "📝 Programar Viagem":
    st.header("📝 Nova Programação")
    df_p = load_data(DB_PASSAGEIROS)
    if df_p.empty:
        st.warning("⚠️ Cadastre o viajante primeiro no menu lateral.")
    else:
        # Seletor fora do form para carregar CC padrão de forma segura
        passag_sel = st.selectbox("Escolha o Passageiro", sorted(df_p["Nome"].tolist()))
        
        # Busca CC padrão de forma segura (previne o erro ValueError)
        cc_row = df_p[df_p["Nome"] == passag_sel]["CC_Padrao"]
        cc_sugerido = cc_row.iloc[0] if not cc_row.empty else LISTA_CC[0]

        with st.form("form_viagem_v6", clear_on_submit=True):
            col1, col2 = st.columns(2)
            data_v = col1.date_input("Data da Viagem", datetime.now())
            mot_v = col1.selectbox("Motorista", ["Ilson", "Antonio"])
            
            try: idx_cc = LISTA_CC.index(cc_sugerido)
            except: idx_cc = 0
            cc_v = col2.selectbox("Centro de Custo (Rateio)", LISTA_CC, index=idx_cc)
            
            saida_v = col1.text_input("Horário Saída")
            voo_v = col2.text_input("Voo / Horário")
            
            st.write("---")
            traj_op = ["P. LACERDA X CUIABÁ", "CUIABÁ X P. LACERDA", "INTERNO", "OUTRO"]
            traj_s = st.selectbox("Trajeto Padrão", traj_op)
            traj_m = st.text_input("Se selecionou 'OUTRO', digite aqui")
            
            hosp_v = st.text_input("Hotel / Destino Final")
            obs_v = st.text_area("Observações (Aparece na Agenda)")
            
            if st.form_submit_button("Salvar Viagem na Agenda Operacional"):
                t_final = traj_m if traj_s == "OUTRO" else traj_s
                nova = pd.DataFrame([{
                    "Data": data_v.strftime('%d/%m/%Y'), "Motorista": mot_v, "Passageiro": passag_sel, 
                    "CC": cc_v, "Saida": saida_v, "Voo": voo_v, "Trajeto": t_final, "Hospedagem": hosp_v,
                    "Observacao": obs_v, "Hotel_RS": 0.0, "Aereo_RS": 0.0, "Combustivel_RS": 0.0, "Total_RS": 0.0
                }])
                pd.concat([load_data(DB_VIAGENS), nova], ignore_index=True).to_csv(DB_VIAGENS, index=False)
                st.success("✅ Viagem registrada!")
                st.rerun()

elif opcao == "👤 Cadastrar Viajante":
    st.header("👤 Cadastro de Funcionário")
    with st.form("form_cad_v6", clear_on_submit=True):
        n = st.text_input("Nome Completo (Sem abreviações)").upper()
        c = st.selectbox("Centro de Custo Padrão", LISTA_CC)
        if st.form_submit_button("Cadastrar Funcionário"):
            if n:
                nova_p = pd.DataFrame([{"Nome": n, "CC_Padrao": c}])
                pd.concat([load_data(DB_PASSAGEIROS), nova_p], ignore_index=True).to_csv(DB_PASSAGEIROS, index=False)
                st.success(f"{n} cadastrado!")
                st.rerun()

elif opcao == "💰 Financeiro":
    st.header("Gestão de Custos e Rateio")
    df = load_data(DB_VIAGENS)
    if not df.empty:
        # Editor com lista suspensa no CC e validação numérica
        df_ed = st.data_editor(
            df,
            column_config={
                "CC": st.column_config.SelectboxColumn("Setor", options=LISTA_CC, required=True),
                "Hotel_RS": st.column_config.NumberColumn("Hotel (R$)", format="R$ %.2f"),
                "Aereo_RS": st.column_config.NumberColumn("Aéreo (R$)", format="R$ %.2f"),
                "Combustivel_RS": st.column_config.NumberColumn("Combust. (R$)", format="R$ %.2f")
            },
            key="ed_aura_v6_fin"
        )
        df_ed["Total_RS"] = df_ed["Hotel_RS"] + df_ed["Aereo_RS"] + df_ed["Combustivel_RS"]
        if st.button("💾 Salvar Alterações Financeiras"):
            save_data(df_ed, DB_VIAGENS)
            st.success("Dados Financeiros Atualizados!")
            st.rerun()
        
        csv_f = df_ed.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 Baixar Relatório Completo", csv_f, "financeiro_aura.csv", key='down_fin_aura_v6')
    else: st.info("Lance as viagens primeiro.")
