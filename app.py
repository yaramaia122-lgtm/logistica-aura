import streamlit as st

try:
    import pandas as pd
    from github import Github
    st.success("Bibliotecas carregadas com sucesso!")
    
    if "GITHUB_TOKEN" in st.secrets:
        st.success("Token encontrado nos Secrets!")
    else:
        st.error("Token NÃO encontrado. Verifique o TOML nos Secrets.")

    # Tenta conectar
    g = Github(st.secrets["GITHUB_TOKEN"])
    repo = g.get_repo("yaramaia122-lgtm/logistica-aura")
    st.write(f"Conectado ao repositório: {repo.full_name}")

except Exception as e:
    st.error(f"O ERRO REAL É: {e}")
