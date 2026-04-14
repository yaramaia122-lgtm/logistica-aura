import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 1. SETUP VISUAL RIGOROSO (STYLEGUIDE AURA)
st.set_page_config(page_title="Aura Minerals - Logística Apoena", layout="wide")

# CSS para forçar Fundo Branco e Cores Institucionais
st.markdown("""
    <style>
    /* Fundo Global */
    .stApp { background-color: #FFFFFF; }
    
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
        border: 2px solid #FFC20E;
        border-radius: 4px;
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
    .stTable { background-color: white; color: #002D5E; }
    </style>
    """, unsafe_allow_html=True)

# 2. INTELIGÊNCIA DE DADOS (BANCO DE DADOS LOCAL)
DB_VIAGENS = "logistica_viagens_v4.csv"
DB_PASSAGEIROS = "cadastro_passageiros_v4.csv"

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

# 3. LISTA DE CENTROS DE CUSTO (INTEGRAL)
LISTA_CC = sorted([
    "210301 - Moagem", "210403 - Detox", "210801 - Laboratório", "211002 - Manut. Mecânica",
    "210405 - Lixiviação Planta", "210101 - Admin. Planta", "211001 - Manut. Elétrica",
    "320101 - Suprimentos", "320301 - RH", "121101 - Geologia Ernesto", "121001 - Planejamento Mina",
    "310501 - Meio Ambiente", "310503 - Segurança Trabalho", "310502 - Saúde", "151101 - Geologia Nosde"
])

# 4. SIDEBAR COM A LOGO NOVA E ESTÁVEL
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
    st.caption("Logística v4.0 | Aura Apoena")

# 5. MÓDULOS
if opcao == "📅 Agenda Motoristas":
    st.header("Agenda de Viagens Operacionais")
    df = load_data(DB_VIAGENS)
    if df.empty:
        st.info("Nenhuma viagem programada.")
    else:
        # Layout limpo para os motoristas (conforme Styleguide)
        view_op = df[["Data", "Motorista", "Passageiro", "Saida", "Voo", "Trajeto", "Hospedagem", "Observacao"]]
        st.table(view_op)
        csv = view_op.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 Baixar Agenda para Motoristas", csv, "agenda_motoristas.csv", "text/csv", key='down_agenda_aura_v4')

elif opcao == "📝 Programar Viagem":
    st.header("📝 Nova Programação")
    df_p = load_data(DB_PASSAGEIROS)
    if df_p.empty:
        st.warning("⚠️ Cadastre o viajante primeiro.")
    else:
        # Seletor fora do form para carregar CC padrão dinamicamente
        nomes = sorted(df_p["Nome"].tolist())
        p_sel = st.selectbox("Escolha o Passageiro", nomes)
        cc_sug = df_p[df_p["Nome"] == p_sel]["CC_Padrao"].iloc[0]

        with st.form("form_viagem_v4_fix"):
            col1, col2 = st.columns(2)
            data_v = col1.date_input("Data da Viagem", datetime.now())
            mot_v = col1.selectbox("Motorista", ["Ilson", "Antonio"])
            
            try: idx_cc = LISTA_CC.index(cc_sug)
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
            
            if st.form_submit_button("Salvar Viagem na Agenda"):
                t_final = traj_m if traj_s == "OUTRO" else traj_s
                nova = pd.DataFrame([{
                    "Data": data_v.strftime('%d/%m/%Y'), "Motorista": mot_v, "Passageiro": p_sel, 
                    "CC": cc_v, "Saida": saida_v, "Voo": voo_v, "Trajeto": t_final, "Hospedagem": hosp_v,
                    "Observacao": obs_v, "Hotel_RS": 0.0, "Aereo_RS": 0.0, "Combustivel_RS": 0.0, "Total_RS": 0.0
                }])
                
                pd.concat([load_data(DB_VIAGENS), nova], ignore_index=True).to_csv(DB_VIAGENS, index=False)
                st.success("Viagem salva na agenda operacional!")
                st.rerun()

elif opcao == "👤 Cadastrar Viajante":
    st.header("👤 Cadastro de Funcionário")
    with st.form("form_p_cad_v4_fix"):
        n = st.text_input("Nome Completo").upper()
        c = st.selectbox("Centro de Custo Padrão", LISTA_CC)
        if st.form_submit_button("Cadastrar Funcionário"):
            if n:
                pd.concat([load_data(DB_PASSAGEIROS), pd.DataFrame([{"Nome": n, "CC_Padrao": c}])], ignore_index=True).to_csv(DB_PASSAGEIROS, index=False)
                st.success(f"{n} cadastrado!")
                st.rerun()

elif opcao == "💰 Financeiro":
    st.header("Gestão de Custos e Rateio")
    df = load_data(DB_VIAGENS)
    if not df.empty:
        # Editor com lista suspensa no CC
        df_ed = st.data_editor(
            df,
            column_config={"CC": st.column_config.SelectboxColumn("CC", options=LISTA_CC)},
            key="ed_v4_fix"
        )
        df_ed["Total_RS"] = df_ed["Hotel_RS"] + df_ed["Aereo_RS"] + df_ed["Combustivel_RS"]
        if st.button("💾 Salvar Alterações Financeiras"):
            save_data(df_ed, DB_VIAGENS)
            st.success("Dados Financeiros Atualizados!")
            st.rerun()
        
        csv_f = df_ed.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 Baixar Relatório Financeiro", csv_f, "financeiro_aura.csv", key='down_fin_aura_v4')
    else: st.info("Lance as viagens primeiro.")
