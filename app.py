import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 1. IDENTIDADE VISUAL CORPORATIVA (AZUL, OCRE E BRANCO)
st.set_page_config(page_title="Logística Aura Minerals", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF !important; }
    [data-testid="stSidebar"] {
        background-color: #002D5E !important;
        border-right: 3px solid #FFC20E;
    }
    [data-testid="stSidebar"] * { color: #FFFFFF !important; }
    .logo-aura {
        filter: drop-shadow(0px 4px 10px rgba(255, 255, 255, 0.4));
        display: block; margin: auto; padding-bottom: 20px;
    }
    h1, h2, h3, label { color: #002D5E !important; font-family: 'Arial Black', sans-serif; }
    .stButton>button {
        background-color: #002D5E; color: white;
        border: 2px solid #FFC20E; border-radius: 5px;
        font-weight: bold; height: 3em; width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. BANCO DE DADOS LOCAL (PERSISTÊNCIA)
DB_VIAGENS = "data_viagens_v32.csv"
DB_PASSAGEIROS = "data_passageiros_v32.csv"

def inicializar_arquivos():
    # Colunas completas e detalhadas
    cols_v = ["Data", "Motorista", "Passageiro", "CC", "Saida", "Voo", "Trajeto", "Hospedagem", "Observacao"]
    cols_p = ["Nome", "Centro_Custo"]
    
    if not os.path.exists(DB_VIAGENS): pd.DataFrame(columns=cols_v).to_csv(DB_VIAGENS, index=False)
    if not os.path.exists(DB_PASSAGEIROS): pd.DataFrame(columns=cols_p).to_csv(DB_PASSAGEIROS, index=False)
    
    v = pd.read_csv(DB_VIAGENS).fillna("")
    p = pd.read_csv(DB_PASSAGEIROS).fillna("")
    return v, p

df_v, df_p = inicializar_arquivos()

LISTA_CC = sorted(["210301 - Moagem", "210403 - Detox", "210801 - Laboratório", "211002 - Manut. Mecânica", "320301 - RH", "310501 - Meio Ambiente"])

# 3. SIDEBAR
with st.sidebar:
    st.markdown("""<div style="text-align: center;"><img src="https://gist.githubusercontent.com/user-attachments/assets/8e0f5228-40b9-4674-9f0f-6df3d57b280c" width="180" class="logo-aura"></div>""", unsafe_allow_html=True)
    st.markdown("---")
    menu = st.radio("MÓDULOS OPERACIONAIS", ["📋 Agenda Motoristas", "📝 Programar Viagem", "👤 Cadastrar Viajante", "💰 Financeiro"])
    st.markdown("---")
    st.write(f"📊 **Base de Dados:** {len(df_v)} viagens / {len(df_p)} passageiros")

# 4. MÓDULOS (DETALHAMENTO TOTAL PARA NÃO FICAR EM BRANCO)

if menu == "📋 Agenda Motoristas":
    st.header("📋 Agenda Operacional de Viagens")
    if not df_v.empty:
        st.dataframe(df_v, use_container_width=True, hide_index=True)
    else:
        st.warning("⚠️ A agenda está vazia porque não há viagens salvas no banco de dados.")
        st.info("💡 Vá ao menu 'Programar Viagem' para realizar o primeiro lançamento.")

elif menu == "📝 Programar Viagem":
    st.header("📝 Detalhamento de Nova Viagem")
    if df_p.empty:
        st.error("❌ ABA EM BRANCO: Você precisa cadastrar um passageiro primeiro para liberar esta função.")
    else:
        with st.form("form_v32", clear_on_submit=True):
            c1, c2 = st.columns(2)
            p_sel = c1.selectbox("Selecione o Passageiro*", sorted(df_p["Nome"].tolist()))
            mot_v = c1.selectbox("Motorista Designado*", ["Ilson", "Antonio"])
            data_v = c1.date_input("Data da Missão", datetime.now())
            
            saida_v = c2.text_input("Horário de Saída (Obrigatório)*")
            voo_v = c2.text_input("Voo / Conexão")
            hosp_v = c2.text_input("Local de Hospedagem")
            
            st.write("---")
            traj_v = st.selectbox("Trajeto Sugerido", ["P. LACERDA X CUIABÁ", "CUIABÁ X P. LACERDA", "INTERNO", "OUTRO"])
            cc_v = st.selectbox("Centro de Custo (Rateio)", LISTA_CC)
            obs_v = st.text_area("Instruções Adicionais para o Motorista")
            
            if st.form_submit_button("✅ SALVAR E REGISTRAR NO BANCO"):
                if not saida_v:
                    st.error("❌ FALHA: Digite o horário de saída antes de salvar.")
                else:
                    nova_v = pd.DataFrame([{
                        "Data": data_v.strftime('%d/%m/%Y'), "Motorista": mot_v, "Passageiro": p_sel,
                        "CC": cc_v, "Saida": saida_v, "Voo": voo_v, "Trajeto": traj_v, 
                        "Hospedagem": hosp_v, "Observacao": obs_v
                    }])
                    pd.concat([df_v, nova_v], ignore_index=True).to_csv(DB_VIAGENS, index=False)
                    st.success(f"✅ REGISTRO CONCLUÍDO: Viagem de {p_sel} salva com sucesso!")
                    st.rerun()

elif menu == "👤 Cadastrar Viajante":
    st.header("👤 Gestão de Passageiros")
    with st.form("cad_v32"):
        n_func = st.text_input("Nome Completo do Colaborador*").upper()
        cc_func = st.selectbox("CC Padrão", LISTA_CC)
        if st.form_submit_button("💾 FINALIZAR CADASTRO"):
            if n_func:
                if n_func in df_p["Nome"].values:
                    st.warning(f"⚠️ O funcionário {n_func} já existe no sistema.")
                else:
                    novo_p = pd.DataFrame([{"Nome": n_func, "Centro_Custo": cc_func}])
                    pd.concat([df_p, novo_p], ignore_index=True).to_csv(DB_PASSAGEIROS, index=False)
                    st.success(f"✅ SUCESSO: {n_func} cadastrado corretamente!")
                    st.rerun()
            else: st.error("❌ ERRO: Digite um nome para cadastrar.")
    st.write("---")
    st.subheader("Lista de Funcionários Ativos")
    st.dataframe(df_p, use_container_width=True, hide_index=True)

elif menu == "💰 Financeiro":
    st.header("💰 Auditoria Financeira")
    if not df_v.empty:
        df_ed = st.data_editor(df_v, use_container_width=True)
        if st.button("💾 ATUALIZAR BANCO DE DADOS"):
            df_ed.to_csv(DB_VIAGENS, index=False)
            st.success("✅ FINANCEIRO: Dados atualizados com sucesso!")
    else:
        st.info("ℹ️ Não há lançamentos para auditoria financeira.")
