import streamlit as st
import pandas as pd
import os
from datetime import datetime

# ----------------------------------------------------------------
# 1. CONFIGURAÇÃO VISUAL RIGOROSA (STYLEGUIDE AURA)
# ----------------------------------------------------------------
st.set_page_config(
    page_title="Aura Minerals - Logística Apoena",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Forçando o CSS para garantir Fundo Branco e Cores Institucionais
st.markdown("""
    <style>
    /* Fundo Global */
    .stApp { background-color: #FFFFFF; }
    
    /* Barra Lateral */
    [data-testid="stSidebar"] {
        background-color: #002D5E !important;
        color: #FFFFFF !important;
    }
    [data-testid="stSidebar"] * { color: #FFFFFF !important; }
    
    /* Títulos e Textos */
    h1, h2, h3, h4, label, p { 
        color: #002D5E !important; 
        font-family: 'Benton Sans', sans-serif !important; 
    }
    
    /* Botões Padrão */
    .stButton>button {
        background-color: #002D5E;
        color: #FFFFFF;
        border: 2px solid #FFC20E;
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
        border: none !important;
        font-weight: 800 !important;
    }
    
    /* Tabelas */
    .stTable, [data-testid="stDataFrame"] {
        background-color: #FFFFFF;
        border: 1px solid #002D5E;
    }
    </style>
    """, unsafe_allow_html=True)

# ----------------------------------------------------------------
# 2. INTELIGÊNCIA DE DADOS (BANCO DE DADOS LOCAL)
# ----------------------------------------------------------------
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

def load_data(file):
    return pd.read_csv(file).fillna("")

def save_data(df, file):
    df.to_csv(file, index=False)

# ----------------------------------------------------------------
# 3. COMPONENTES DE INTERFACE
# ----------------------------------------------------------------
LISTA_CC = sorted([
    "210301 - Moagem", "210403 - Detox", "210801 - Laboratório", "211002 - Manut. Mecânica",
    "210405 - Lixiviação / Cianetação", "210101 - Admin. Planta", "211001 - Manut. Elétrica",
    "211003 - Oficina Manut. Planta", "210201 - Britagem Primária", "210604 - Fundição",
    "310101 - Almoxarifado", "320401 - Contabilidade", "310701 - Serviços Gerais",
    "320601 - Gestão Contratos", "320101 - Suprimentos", "320502 - TI", "320301 - RH",
    "121101 - Geologia Ernesto", "121001 - Planejamento Mina", "110101 - Adm. Mina",
    "310501 - Meio Ambiente", "310503 - Segurança Trabalho", "310502 - Saúde",
    "151101 - Geologia Nosde", "150101 - Adm. Mina Nosde"
])

# Sidebar com Identidade Visual
with st.sidebar:
    st.image("https://auraminerals.com/wp-content/themes/aura-minerals/assets/img/logo-aura.png", width=200)
    st.markdown("---")
    st.markdown("### PAINEL DE CONTROLE")
    opcao = st.radio(
        "Selecione o Módulo:",
        ["📋 Agenda Operacional", "📝 Programar Viagem", "👤 Cadastro de Viajantes", "💰 Gestão Financeira"]
    )
    st.markdown("---")
    st.caption("Sistema de Logística v4.0 | Aura Apoena")

# ----------------------------------------------------------------
# 4. MÓDULOS DO SISTEMA
# ----------------------------------------------------------------

# --- MÓDULO 1: AGENDA (VISÃO MOTORISTA) ---
if opcao == "📋 Agenda Operacional":
    st.title("Agenda Operacional de Viagens")
    df = load_data(DB_VIAGENS)
    
    if df.empty:
        st.info("Nenhuma viagem programada no momento.")
    else:
        # Layout focado no Motorista (conforme solicitado)
        view_op = df[["Data", "Motorista", "Passageiro", "Saida", "Voo", "Trajeto", "Hospedagem", "Observacao"]]
        st.table(view_op)
        
        # Exportação padronizada
        csv = view_op.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 EXPORTAR AGENDA SEMANAL",
            data=csv,
            file_name=f"Agenda_Logistica_{datetime.now().strftime('%d_%m_%Y')}.csv",
            mime="text/csv"
        )

# --- MÓDULO 2: PROGRAMAÇÃO ---
elif opcao == "📝 Programar Viagem":
    st.title("Programação de Nova Viagem")
    df_p = load_data(DB_PASSAGEIROS)
    
    if df_p.empty:
        st.error("Erro: Não há viajantes cadastrados. Vá ao módulo 'Cadastro de Viajantes' primeiro.")
    else:
        # Seleção de Passageiro para puxar o CC padrão automaticamente
        passag = st.selectbox("Selecione o Passageiro:", sorted(df_p["Nome"].tolist()))
        cc_default = df_p[df_p["Nome"] == passag]["CC_Padrao"].iloc[0]

        with st.form("form_viagem", clear_on_submit=True):
            c1, c2 = st.columns(2)
            
            with c1:
                data_v = st.date_input("Data da Viagem", datetime.now())
                mot_v = st.selectbox("Motorista Designado", ["Ilson", "Antonio", "Terceirizado"])
                saida_v = st.text_input("Horário de Saída (ex: 06:00)")
                
            with c2:
                # Centro de Custo Flexível
                try: idx_cc = LISTA_CC.index(cc_default)
                except: idx_cc = 0
                cc_v = st.selectbox("Centro de Custo (Rateio)", LISTA_CC, index=idx_cc)
                voo_v = st.text_input("Voo / Horário Chegada")
                traj_v = st.selectbox("Trajeto Padrão", ["P. LACERDA X CUIABÁ", "CUIABÁ X P. LACERDA", "INTERNO", "OUTRO"])
            
            traj_outro = st.text_input("Se selecionou 'OUTRO', especifique o trajeto:")
            hosp_v = st.text_input("Destino Final / Hotel (ex: Hotel Cerrados)")
            obs_v = st.text_area("Observações Adicionais (Aparece na Agenda)")
            
            if st.form_submit_button("✅ CONFIRMAR PROGRAMAÇÃO"):
                trajeto_final = traj_outro if traj_v == "OUTRO" else traj_v
                nova_v = pd.DataFrame([{
                    "Data": data_v.strftime('%d/%m/%Y'), "Motorista": mot_v, "Passageiro": passag,
                    "CC": cc_v, "Saida": saida_v, "Voo": voo_v, "Trajeto": trajeto_final,
                    "Hospedagem": hosp_v, "Observacao": obs_v, "Hotel_RS": 0.0, 
                    "Aereo_RS": 0.0, "Combustivel_RS": 0.0, "Total_RS": 0.0
                }])
                
                db_atual = load_data(DB_VIAGENS)
                new_db = pd.concat([db_atual, nova_v], ignore_index=True)
                save_data(new_db, DB_VIAGENS)
                st.success(f"Viagem de {passag} salva com sucesso!")
                st.rerun()

# --- MÓDULO 3: CADASTRO ---
elif opcao == "👤 Cadastro de Viajantes":
    st.title("Cadastro de Colaboradores")
    with st.form("form_cadastro", clear_on_submit=True):
        nome_c = st.text_input("Nome Completo do Viajante:").upper()
        cc_p = st.selectbox("Centro de Custo Principal:", LISTA_CC)
        
        if st.form_submit_button("💾 CADASTRAR VIAJANTE"):
            if nome_c:
                db_p = load_data(DB_PASSAGEIROS)
                if nome_c in db_p["Nome"].values:
                    st.warning("Este passageiro já está cadastrado.")
                else:
                    novo_p = pd.DataFrame([{"Nome": nome_c, "CC_Padrao": cc_p}])
                    save_data(pd.concat([db_p, novo_p], ignore_index=True), DB_PASSAGEIROS)
                    st.success(f"Cadastro de {nome_c} realizado!")
            else:
                st.error("O campo Nome é obrigatório.")

# --- MÓDULO 4: FINANCEIRO ---
elif opcao == "💰 Gestão Financeira":
    st.title("Controle Financeiro e Rateio de Custos")
    df_f = load_data(DB_VIAGENS)
    
    if df_f.empty:
        st.info("Aguardando lançamentos de viagens para gerar dados financeiros.")
    else:
        st.markdown("### Edição de Custos por Centro de Custo")
        # Editor avançado com lista suspensa para CC e validação numérica
        df_editado = st.data_editor(
            df_f,
            column_config={
                "CC": st.column_config.SelectboxColumn("Setor (CC)", options=LISTA_CC, required=True),
                "Hotel_RS": st.column_config.NumberColumn("Hotel (R$)", min_value=0, format="R$ %.2f"),
                "Aereo_RS": st.column_config.NumberColumn("Aéreo (R$)", min_value=0, format="R$ %.2f"),
                "Combustivel_RS": st.column_config.NumberColumn("Combust. (R$)", min_value=0, format="R$ %.2f"),
                "Total_RS": st.column_config.NumberColumn("Total (R$)", disabled=True, format="R$ %.2f")
            },
            disabled=["Data", "Passageiro", "Motorista"],
            use_container_width=True,
            key="financeiro_editor"
        )
        
        # Cálculo automático do Total
        df_editado["Total_RS"] = df_editado["Hotel_RS"] + df_editado["Aereo_RS"] + df_editado["Combustivel_RS"]
        
        if st.button("💾 SALVAR ALTERAÇÕES FINANCEIRAS"):
            save_data(df_editado, DB_VIAGENS)
            st.success("Financeiro atualizado com sucesso!")
            st.rerun()
            
        st.markdown("---")
        csv_fin = df_editado.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 BAIXAR RELATÓRIO FINANCEIRO (RATEIO)", csv_fin, "Financeiro_Logistica_Aura.csv", key="down_fin")
