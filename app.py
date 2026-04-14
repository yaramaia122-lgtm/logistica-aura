import streamlit as st
import pandas as pd
import os
from datetime import datetime
import base64

# 1. FORÇAR TEMA CLARO E CORES AURA (RIGOROSO)
st.set_page_config(page_title="Aura Minerals - Logística", layout="wide")

st.markdown("""
    <style>
    /* Bloqueia o Modo Escuro e força fundo branco */
    .stApp { background-color: white !important; }
    [data-testid="stSidebar"] { background-color: #002D5E !important; }
    [data-testid="stSidebar"] * { color: white !important; }
    
    /* Títulos e Textos em Azul Aura */
    h1, h2, h3, h4, label, p, span { color: #002D5E !important; font-family: 'Benton Sans', sans-serif; }
    
    /* Botões Padrão Aura */
    .stButton>button { background-color: #002D5E; color: white; border: 2px solid #FFC20E; border-radius: 4px; }
    .stDownloadButton>button { background-color: #FFC20E !important; color: #002D5E !important; font-weight: bold; }
    
    /* Tabelas operacionais */
    .stTable { background-color: white !important; border: 1px solid #002D5E; }
    </style>
    """, unsafe_allow_html=True)

# 2. FUNÇÃO PARA CONVERTER IMAGEM EM CÓDIGO (BASE64)
def carregar_logo_local(caminho_img):
    if os.path.exists(caminho_img):
        with open(caminho_img, "rb") as f:
            data = f.read()
            return base64.b64encode(data).decode()
    return None

# 3. BASE DE DADOS (VERSÃO LIMPA PARA EVITAR VALUEERROR)
DB_V = "logistica_aura_v8.csv"
DB_P = "passageiros_aura_v8.csv"

def inicializar_dados():
    if not os.path.exists(DB_V):
        pd.DataFrame(columns=["Data", "Motorista", "Passageiro", "CC", "Saida", "Voo", "Trajeto", "Hospedagem", "Observacao", "Hotel_RS", "Aereo_RS", "Combust_RS", "Total_RS"]).to_csv(DB_V, index=False)
    if not os.path.exists(DB_P):
        pd.DataFrame(columns=["Nome", "CC_Padrao"]).to_csv(DB_P, index=False)
    return pd.read_csv(DB_V).fillna(""), pd.read_csv(DB_P).fillna("")

df_v, df_p = inicializar_dados()

LISTA_CC = sorted([
    "210301 - Moagem", "210403 - Detox", "210801 - Laboratório", "211002 - Manut. Mecânica",
    "210405 - Lixiviação Planta", "210101 - Admin. Planta", "211001 - Manut. Elétrica",
    "320101 - Suprimentos", "320301 - RH", "121101 - Geologia Ernesto", "151101 - Geologia Nosde",
    "310501 - Meio Ambiente", "310503 - Segurança Trabalho", "310502 - Saúde"
])

# 4. SIDEBAR COM A LOGO (MÉTODO INFALÍVEL)
with st.sidebar:
    # O código procura o ficheiro que subiu: "Aura (Azul e Ocre).png"
    logo_b64 = carregar_logo_local("Aura (Azul e Ocre).png")
    
    if logo_b64:
        st.markdown(f'<img src="data:image/png;base64,{logo_b64}" width="100%">', unsafe_allow_html=True)
    else:
        st.write("### AURA MINERALS") # Texto reserva caso a imagem seja apagada do GitHub
    
    st.markdown("---")
    menu = st.radio("MENU PRINCIPAL", ["📋 Agenda Motoristas", "📝 Programar Viagem", "👤 Cadastrar Viajante", "💰 Financeiro"])

# 5. MÓDULOS OPERACIONAIS

if menu == "📋 Agenda Motoristas":
    st.header("Agenda Operacional de Viagens")
    if not df_v.empty:
        # Colunas rigorosas para o motorista
        agenda = df_v[["Data", "Motorista", "Passageiro", "Saida", "Voo", "Trajeto", "Hospedagem", "Observacao"]]
        st.table(agenda)
        csv = agenda.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 Exportar Agenda (CSV)", csv, "agenda_logistica.csv", "text/csv")
    else: st.info("Nenhuma viagem programada.")

elif menu == "📝 Programar Viagem":
    st.header("Nova Programação")
    if df_p.empty:
        st.warning("Cadastre um viajante primeiro.")
    else:
        lista_viajantes = sorted(df_p["Nome"].tolist())
        nome_sel = st.selectbox("Selecione o Passageiro", lista_viajantes)
        
        # Proteção contra erros de busca
        cc_row = df_p[df_p["Nome"] == nome_sel]["CC_Padrao"]
        cc_sug = cc_row.iloc[0] if not cc_row.empty else LISTA_CC[0]

        with st.form("form_v8"):
            c1, c2 = st.columns(2)
            data = c1.date_input("Data da Viagem")
            mot = c1.selectbox("Motorista", ["Ilson", "Antonio"])
            
            try: idx = LISTA_CC.index(cc_sug)
            except: idx = 0
            
            cc_v = c2.selectbox("CC (Rateio)", LISTA_CC, index=idx)
            saida = c1.text_input("Horário de Saída")
            voo = c2.text_input("Voo / Horário Chegada")
            
            st.write("---")
            traj = st.selectbox("Trajeto Principal", ["P. LACERDA X CUIABÁ", "CUIABÁ X P. LACERDA", "INTERNO", "OUTRO"])
            traj_m = st.text_input("Se selecionou 'OUTRO', especifique:")
            hosp = st.text_input("Hotel / Destino Final")
            obs = st.text_area("Observações para o Motorista")
            
            if st.form_submit_button("Salvar na Agenda"):
                t_f = traj_m if traj == "OUTRO" else traj
                nova = pd.DataFrame([{
                    "Data": data.strftime('%d/%m/%Y'), "Motorista": mot, "Passageiro": nome_sel, 
                    "CC": cc_v, "Saida": saida, "Voo": voo, "Trajeto": t_f, "Hospedagem": hosp,
                    "Observacao": obs, "Hotel_RS": 0.0, "Aereo_RS": 0.0, "Combust_RS": 0.0, "Total_RS": 0.0
                }])
                pd.concat([df_v, nova], ignore_index=True).to_csv(DB_V, index=False)
                st.success("✅ Viagem salva!")
                st.rerun()

elif menu == "👤 Cadastrar Viajante":
    st.header("Cadastro de Funcionários")
    with st.form("form_p8"):
        n = st.text_input("Nome Completo").upper()
        c = st.selectbox("Centro de Custo Padrão", LISTA_CC)
        if st.form_submit_button("Cadastrar Funcionário"):
            if n:
                pd.concat([df_p, pd.DataFrame([{"Nome": n, "CC_Padrao": c}])], ignore_index=True).to_csv(DB_P, index=False)
                st.success("Cadastrado com sucesso!")
                st.rerun()

elif menu == "💰 Financeiro":
    st.header("Gestão Financeira e Rateio")
    if not df_v.empty:
        # Editor com lista suspensa e cálculo automático
        df_ed = st.data_editor(df_v, column_config={"CC": st.column_config.SelectboxColumn("Setor", options=LISTA_CC)})
        df_ed["Total_RS"] = df_ed["Hotel_RS"] + df_ed["Aereo_RS"] + df_ed["Combust_RS"]
        
        if st.button("💾 Salvar Alterações Financeiras"):
            df_ed.to_csv(DB_V, index=False)
            st.success("Valores atualizados!")
            st.rerun()
        
        st.download_button("📥 Baixar Relatório", df_ed.to_csv(index=False).encode('utf-8-sig'), "financeiro_aura.csv")
