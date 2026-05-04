import streamlit as st
from github import Github, Auth
from datetime import datetime

# 1. Interface - Sua Estrutura Original
st.image("logo.png") 
st.title("🚚 Logística Aura - Gestão de Viagens")
st.subheader("Cadastro de Programação")

with st.form("form_logistica"):
    col1, col2 = st.columns(2)
    
    with col1:
        motorista = st.text_input("Nome do Motorista")
        placa = st.text_input("Placa do Veículo")
    
    with col2:
        origem = st.text_input("Cidade de Origem")
        destino = st.text_input("Cidade de Destino")
    
    data_viagem = st.date_input("Data da Viagem", datetime.now())
    observacoes = st.text_area("Observações Adicionais")
    
    submit = st.form_submit_button("Salvar Programação")

# 2. Lógica de Salvar (Com o fix do GitHub)
if submit:
    if motorista and placa:
        try:
            # AQUI ESTÁ A CORREÇÃO DO ERRO 401
            auth = Auth.Token(st.secrets["GITHUB_TOKEN"])
            g = Github(auth=auth)
            
            # Conexão com seu repositório
            repo = g.get_repo("yaramaia122-lgtm/logistica-aura")
            
            # Dados para salvar
            nova_viagem = f"\n{motorista},{placa},{origem},{destino},{data_viagem}"
            path = "viagens_programadas.csv"
            
            try:
                # Tenta atualizar o arquivo se ele já existir
                contents = repo.get_contents(path)
                repo.update_file(contents.path, "Atualizando viagens", contents.decoded_content.decode() + nova_viagem, contents.sha)
            except:
                # Cria o arquivo se for a primeira vez
                repo.create_file(path, "Criando arquivo", "Motorista,Placa,Origem,Destino,Data" + nova_viagem)
            
            st.success("Viagem programada com sucesso!")
            
        except Exception as e:
            st.error(f"Erro ao gravar dados: {e}")
    else:
        st.warning("Por favor, preencha os campos obrigatórios (Motorista e Placa).")
