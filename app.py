import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# Configuração da Página
st.set_page_config(page_title="Aura Logística Web", layout="wide")

# Conexão com o Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# Mapeamento de Centro de Custo (PDF)
MAPA_CC = {
    "Moagem": "210301", "Detox": "210403", "Laboratório": "210801",
    "Manutenção Mecânica Planta": "211002", "Administração Planta": "210101",
    "Geologia Operacional": "121101", "Meio Ambiente": "310501",
    "Segurança do Trabalho": "310503", "Saude": "310502"
}

st.title("🚛 Sistema de Logística e Custos Aura (Web)")

menu = st.sidebar.radio("Navegação", ["Painel do Motorista", "Lançar Viagem/Logística", "Inserir Custos (Combustível/Hotel)", "Cadastro de Passageiros"])

# --- CADASTRO DE PASSAGEIROS ---
if menu == "Cadastro de Passageiros":
    st.header("👥 Cadastro de Equipe")
    with st.form("cadastro_form"):
        nome = st.text_input("Nome Completo")
        area = st.selectbox("Área", sorted(list(MAPA_CC.keys())))
        if st.form_submit_button("Salvar na Nuvem"):
            df_existente = conn.read(worksheet="Passageiros")
            novo_p = pd.DataFrame([{"Nome": nome, "Area": area, "Codigo": MAPA_CC[area]}])
            df_final = pd.concat([df_existente, novo_p], ignore_index=True)
            conn.update(worksheet="Passageiros", data=df_final)
            st.success(f"{nome} cadastrado!")

# --- LANÇAR LOGÍSTICA (MOTORISTA VÊ NA HORA) ---
elif menu == "Lançar Viagem/Logística":
    st.header("🕒 Programação Operacional")
    df_p = conn.read(worksheet="Passageiros")
    
    if df_p.empty:
        st.warning("Cadastre passageiros primeiro.")
    else:
        with st.form("logistica_form"):
            col1, col2 = st.columns(2)
            data_v = col1.date_input("Data da Viagem")
            trajeto = col1.selectbox("Trajeto", ["PONTES E LACERDA X CUIABÁ", "CUIABÁ X PONTES E LACERDA"])
            motorista = col2.selectbox("Motorista", ["Ilson", "Antonio"])
            veiculo = col2.selectbox("Veículo", ["SW4 BRANCA", "SW4 PRATA", "VAN"])
            
            passageiros_sel = st.multiselect("Selecione os Passageiros", df_p['Nome'].unique())
            
            detalhes = []
            if passageiros_sel:
                for p in passageiros_sel:
                    c1, c2 = st.columns(2)
                    h_s = c1.time_input(f"Saída de {p}", key=f"s_{p}")
                    h_v = c2.time_input(f"Voo de {p}", key=f"v_{p}")
                    detalhes.append({"p": p, "s": h_s.strftime("%H:%M"), "v": h_v.strftime("%H:%M")})

            if st.form_submit_button("Confirmar Programação"):
                viagem_id = datetime.now().strftime("%Y%m%d%H%M%S")
                df_viagens = conn.read(worksheet="Viagens")
                novas_linhas = []
                for d in detalhes:
                    info = df_p[df_p['Nome'] == d['p']].iloc[0]
                    novas_linhas.append({
                        "ID": viagem_id, "Data": str(data_v), "Motorista": motorista,
                        "Passageiro": d['p'], "Area": info['Area'], "Saida": d['s'],
                        "Voo": d['v'], "Trajeto": trajeto, "Veiculo": veiculo, "Status": "Pendente Custo"
                    })
                df_updated = pd.concat([df_viagens, pd.DataFrame(novas_linhas)], ignore_index=True)
                conn.update(worksheet="Viagens", data=df_updated)
                st.success("Logística publicada! Motorista já pode visualizar.")

# --- INSERIR CUSTOS (COMBUSTÍVEL CHEGA DEPOIS) ---
elif menu == "Inserir Custos (Combustível/Hotel)":
    st.header("💰 Rateio Financeiro")
    df_v = conn.read(worksheet="Viagens")
    
    if not df_v.empty:
        viagens_pendentes = df_v[df_v['Status'] == "Pendente Custo"]['ID'].unique()
        viagem_sel = st.selectbox("Selecione a Viagem para fechar custos", viagens_pendentes)
        
        if viagem_sel:
            pess_na_viagem = df_v[df_v['ID'] == viagem_sel]['Passageiro'].tolist()
            st.write(f"Passageiros no carro: {len(pess_na_viagem)}")
            
            v_combustivel = st.number_input("Valor Total Combustível/Traslado (R$)", min_value=0.0)
            rateio_carro = v_combustivel / len(pess_na_viagem)
            
            custos_ind = []
            for p in pess_na_viagem:
                st.subheader(f"Custos Individuais: {p}")
                col1, col2 = st.columns(2)
                h = col1.number_input(f"Hotel para {p}", key=f"h_{p}")
                a = col2.number_input(f"Aéreo para {p}", key=f"a_{p}")
                custos_ind.append({"p": p, "h": h, "a": a})
            
            if st.button("Finalizar e Enviar para o Financeiro"):
                for c in custos_ind:
                    idx = df_v[(df_v['ID'] == viagem_sel) & (df_v['Passageiro'] == c['p'])].index
                    df_v.loc[idx, 'Custo_Carro'] = rateio_carro
                    df_v.loc[idx, 'Hotel'] = c['h']
                    df_v.loc[idx, 'Aereo'] = c['a']
                    df_v.loc[idx, 'Total'] = rateio_carro + c['h'] + c['a']
                    df_v.loc[idx, 'Status'] = "Finalizado"
                
                conn.update(worksheet="Viagens", data=df_v)
                st.balloons()
                st.success("Custos rateados por área!")

# --- PAINEL DO MOTORISTA ---
elif menu == "Painel do Motorista":
    st.header("🚗 Agenda de Saídas")
    df = conn.read(worksheet="Viagens")
    if not df.empty:
        hoje = str(datetime.today().date())
        agenda = df[df['Data'] == hoje]
        st.write(f"Hoje: {datetime.today().strftime('%d/%m/%Y')}")
        st.table(agenda[['Saida', 'Passageiro', 'Voo', 'Trajeto', 'Motorista', 'Veiculo']])
