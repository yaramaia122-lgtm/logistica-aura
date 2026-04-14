import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 1. IDENTIDADE VISUAL RIGOROSA (STYLEGUIDE AURA)
st.set_page_config(page_title="Aura Minerals - Logística Apoena", layout="wide")

# CSS para forçar fundo branco, remover modo escuro e usar cores oficiais
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF !important; }
    [data-testid="stSidebar"] { background-color: #002D5E !important; }
    [data-testid="stSidebar"] * { color: #FFFFFF !important; }
    h1, h2, h3, h4, label, p, span { color: #002D5E !important; font-family: 'Benton Sans', sans-serif !important; }
    .stButton>button { background-color: #002D5E; color: white; border: 2px solid #FFC20E; border-radius: 4px; }
    .stDownloadButton>button { background-color: #FFC20E !important; color: #002D5E !important; font-weight: bold; border: none; }
    .stTable { background-color: #FFFFFF; border: 1px solid #002D5E; }
    </style>
    """, unsafe_allow_html=True)

# 2. BANCO DE DADOS (VERSÃO V5 - SEGURANÇA TOTAL)
DB_V = "logistica_v5_viagens.csv"
DB_P = "logistica_v5_passageiros.csv"

def carregar(file, cols):
    if os.path.exists(file):
        try:
            df = pd.read_csv(file)
            return df if not df.empty else pd.DataFrame(columns=cols)
        except: return pd.DataFrame(columns=cols)
    return pd.DataFrame(columns=cols)

def salvar(df, file): df.to_csv(file, index=False)

# Estrutura de colunas para evitar erros de índice
COLS_V = ["Data", "Motorista", "Passageiro", "CC", "Saida", "Voo", "Trajeto", "Hospedagem", "Observacao", "Hotel_RS", "Aereo_RS", "Combustivel_RS", "Total_RS"]
df_v = carregar(DB_V, COLS_V)
df_p = carregar(DB_P, ["Nome", "CC_Padrao"])

# LISTA OFICIAL DE CENTROS DE CUSTO (CONFORME SEU PDF/MAPA)
LISTA_CC = sorted([
    "210301 - Moagem", "210403 - Detox", "210801 - Laboratório", "211002 - Manut. Mecânica",
    "210405 - Lixiviação Planta", "210101 - Admin. Planta", "211001 - Manut. Elétrica",
    "320101 - Suprimentos", "320301 - RH", "121101 - Geologia Ernesto", "151101 - Geologia Nosde",
    "310501 - Meio Ambiente", "310503 - Segurança Trabalho", "310502 - Saúde", "310801 - Segurança Patrimonial",
    "121001 - Planejamento Mina", "150101 - Adm. de Mina - Nosde"
])

# 3. BARRA LATERAL (LOGO E NAVEGAÇÃO)
with st.sidebar:
    # Logo da imagem que me enviaste (Aura Azul e Ocre)
    st.image("https://gist.githubusercontent.com/user-attachments/assets/8e0f5228-40b9-4674-9f0f-6df3d57b280c", use_container_width=True)
    st.markdown("---")
    menu = st.radio("SISTEMA DE LOGÍSTICA", ["📋 Agenda Motoristas", "📝 Programar Viagem", "👤 Cadastrar Viajante", "💰 Gestão Financeira"])
    st.markdown("---")
    st.caption("Aura Minerals - Logística v5.0")

# 4. MÓDULOS

# --- MÓDULO: AGENDA OPERACIONAL ---
if menu == "📋 Agenda Motoristas":
    st.header("Agenda de Viagens Operacionais")
    if not df_v.empty:
        agenda = df_v[["Data", "Motorista", "Passageiro", "Saida", "Voo", "Trajeto", "Hospedagem", "Observacao"]]
        st.table(agenda)
        csv = agenda.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 Baixar Agenda Semanal (CSV)", csv, "agenda_logistica.csv", "text/csv")
    else: st.info("Nenhuma viagem programada.")

# --- MÓDULO: PROGRAMAÇÃO (BLINDADO CONTRA VALUEERROR) ---
elif menu == "📝 Programar Viagem":
    st.header("Nova Programação")
    if df_p.empty:
        st.warning("⚠️ Primeiro, cadastre os viajantes no menu 'Cadastrar Viajante'.")
    else:
        nomes_lista = sorted(df_p["Nome"].tolist())
        passag_sel = st.selectbox("Selecione o Passageiro", nomes_lista)
        
        # Busca CC padrão de forma segura (previne o erro de '0 is not in list')
        cc_row = df_p[df_p["Nome"] == passag_sel]["CC_Padrao"]
        cc_sugerido = cc_row.iloc[0] if not cc_row.empty else LISTA_CC[0]

        with st.form("form_viagem_v5"):
            c1, c2 = st.columns(2)
            data_v = c1.date_input("Data da Viagem")
            mot_v = c1.selectbox("Motorista", ["Ilson", "Antonio"])
            
            # Garante que o índice exista na lista de CCs
            try: idx_cc = LISTA_CC.index(cc_sugerido)
            except: idx_cc = 0
            
            cc_v = c2.selectbox("Centro de Custo (Pode alterar)", LISTA_CC, index=idx_cc)
            saida_v = c1.text_input("Horário Saída")
            voo_v = c2.text_input("Voo / Horário")
            
            st.write("---")
            traj_op = ["P. LACERDA X CUIABÁ", "CUIABÁ X P. LACERDA", "INTERNO", "OUTRO"]
            traj_s = st.selectbox("Trajeto Padrão", traj_op)
            traj_m = st.text_input("Se selecionou 'OUTRO', digite aqui")
            
            hosp_v = st.text_input("Informação de Hotel / Destino")
            obs_v = st.text_area("Observações (Informações para o motorista)")
            
            if st.form_submit_button("✅ Salvar Viagem"):
                t_f = traj_m if traj_s == "OUTRO" else traj_s
                nova = pd.DataFrame([{
                    "Data": data_v.strftime('%d/%m/%Y'), "Motorista": mot_v, "Passageiro": passag_sel, 
                    "CC": cc_v, "Saida": saida_v, "Voo": voo_v, "Trajeto": t_f, "Hospedagem": hosp_v,
                    "Observacao": obs_v, "Hotel_RS": 0.0, "Aereo_RS": 0.0, "Combustivel_RS": 0.0, "Total_RS": 0.0
                }])
                salvar(pd.concat([df_v, nova], ignore_index=True), DB_V)
                st.success("Viagem salva com sucesso!")
                st.rerun()

# --- MÓDULO: CADASTRO ---
elif menu == "👤 Cadastrar Viajante":
    st.header("Cadastro de Colaboradores")
    with st.form("form_cad_v5"):
        n = st.text_input("Nome Completo (Sem abreviações)").upper()
        c = st.selectbox("Centro de Custo Padrão", LISTA_CC)
        if st.form_submit_button("💾 Cadastrar"):
            if n:
                novo_p = pd.DataFrame([{"Nome": n, "CC_Padrao": c}])
                salvar(pd.concat([df_p, novo_p], ignore_index=True), DB_P)
                st.success(f"{n} cadastrado!")
                st.rerun()
            else: st.error("O nome é obrigatório.")

# --- MÓDULO: FINANCEIRO ---
elif menu == "💰 Gestão Financeira":
    st.header("Gestão Financeira e Rateio")
    if not df_v.empty:
        df_ed = st.data_editor(
            df_v,
            column_config={
                "CC": st.column_config.SelectboxColumn("Setor (CC)", options=LISTA_CC, required=True),
                "Hotel_RS": st.column_config.NumberColumn("Hotel (R$)", format="%.2f"),
                "Aereo_RS": st.column_config.NumberColumn("Aéreo (R$)", format="%.2f"),
                "Combustivel_RS": st.column_config.NumberColumn("Combust. (R$)", format="%.2f")
            },
            key="editor_aura_v5"
        )
        df_ed["Total_RS"] = df_ed["Hotel_RS"] + df_ed["Aereo_RS"] + df_ed["Combustivel_RS"]
        
        if st.button("💾 Salvar Alterações"):
            salvar(df_ed, DB_V)
            st.success("Financeiro atualizado!")
            st.rerun()
        
        csv_f = df_ed.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 Exportar Relatório Financeiro", csv_f, "financeiro_aura.csv")
