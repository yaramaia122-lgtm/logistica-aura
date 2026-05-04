import streamlit as st
from github import Github, Auth
import pandas as pd
from datetime import datetime

# 1. Configuração da Página e Estética (Visual Moderno e Profissional)
st.set_page_config(page_title="Logística Aura", page_icon="🚚", layout="centered")

# CSS personalizado para o Azul Marinho e Alinhamento
st.markdown("""
    <style>
    .stButton>button {
        background-color: #000080; /* Azul Marinho */
        color: white;
        border-radius: 10px;
        width: 100%;
    }
    .stTextInput>div>div>input {
        border-color: #add8e6; /* Azul Claro */
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Conexão Segura com o GitHub (Resolvendo o erro 401)
def conectar_github():
    try:
        # Pega o token do segredo que você salvou no Streamlit Cloud
        token = st.secrets["GITHUB_TOKEN"]
        auth = Auth.Token(token)
        return Github(auth=auth)
    except Exception as e:
        st.error("Erro de conexão: Verifique o GITHUB_TOKEN nos Secrets do Streamlit.")
        return None

# 3. Interface do Aplicativo
st.image("logo.png", width=200)
st.title("🚚 Logística Aura - Gestão de Viagens")
st.subheader("Cadastro de Programação")

# Estrutura mapeada e alinhada dos campos
with st.form("form_logistica", clear_on_submit=True):
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

# 4. Gravação das Informações (Persistência de Dados)
if submit:
    if motorista and placa:
        g = conectar_github()
        if g:
            try:
                # Substitua pelo SEU usuário e nome do repositório
                repo = g.get_repo("yaramaia122-lgtm/logistica-aura")
                
                # Criando os dados para salvar
                nova_viagem = {
                    "Motorista": motorista,
                    "Placa": placa,
                    "Origem": origem,
                    "Destino": destino,
                    "Data": str(data_viagem),
                    "Registro": datetime.now().strftime("%d/%m/%Y %H:%M")
                }
                
                # Logística para salvar em um CSV no GitHub
                path = "viagens_programadas.csv"
                conteudo_novo = f"\n{nova_viagem['Motorista']},{nova_viagem['Placa']},{nova_viagem['Origem']},{nova_viagem['Destino']},{nova_viagem['Data']}"
                
                try:
                    contents = repo.get_contents(path)
                    repo.update_file(contents.path, "Atualizando viagens", contents.decoded_content.decode() + conteudo_novo, contents.sha)
                except:
                    repo.create_file(path, "Criando arquivo de viagens", "Motorista,Placa,Origem,Destino,Data" + conteudo_novo)
                
                st.success("✅ Viagem programada com sucesso!") # Feedback profissional
                
            except Exception as e:
                st.error(f"Erro ao gravar dados: {e}")
    else:
        st.warning("Por favor, preencha os campos obrigatórios (Motorista e Placa).")

---
### O que mudou?
*   **Segurança:** Usei o `github.Auth.Token` para eliminar os avisos de erro e garantir que o seu token funcione corretamente.
*   **Organização:** Usei `st.form` e `st.columns` para que os campos não fiquem espalhados e desorganizados como antes.
*   **Identidade Visual:** Adicionei um bloco de CSS para que os botões sigam o **azul marinho** que você escolheu.

**Lembrete:** Para este código rodar sem erro 401, o seu token deve estar colado dentro do menu **Secrets** lá no painel do Streamlit Cloud, conforme combinamos!
