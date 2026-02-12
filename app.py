import streamlit as st
import requests
import os
import pandas as pd
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Assistente IA Pro", page_icon="🤖", layout="wide")
st.title("🤖 Assistente IA Online")

# --- CONFIGURAÇÕES DE API (ATUALIZADO PARA ROUTER) ---
HF_TOKEN = os.getenv("HF_TOKEN")
# A URL correta que o erro 410 solicitou
API_URL = "https://router.huggingface.co/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {HF_TOKEN}",
    "Content-Type": "application/json",
}

# --- PERSISTÊNCIA DE DADOS ---
if "tabela_dados" not in st.session_state:
    st.session_state.tabela_dados = pd.DataFrame(columns=["Data/Hora", "Pergunta", "Resposta"])

def perguntar_ia(pergunta):
    # O Router exige o formato de mensagens (chat completions)
    payload = {
        "model": "mistralai/Mistral-7B-Instruct-v0.3", # Modelo robusto
        "messages": [
            {"role": "user", "content": pergunta}
        ],
        "max_tokens": 500,
        "stream": False
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            # Extração correta do conteúdo no formato Chat
            return data["choices"][0]["message"]["content"]
        else:
            return f"Erro {response.status_code}: {response.text}"
    except Exception as e:
        return f"Erro de conexão: {str(e)}"

# --- INTERFACE ---
pergunta_usuario = st.text_input("Digite sua pergunta:", key="input_pergunta")

if st.button("Enviar") and pergunta_usuario:
    with st.spinner("IA processando..."):
        resposta_ia = perguntar_ia(pergunta_usuario)
        
        # Salva e preserva os dados na tabela
        nova_linha = pd.DataFrame([{
            "Data/Hora": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "Pergunta": pergunta_usuario,
            "Resposta": resposta_ia
        }])
        
        st.session_state.tabela_dados = pd.concat([st.session_state.tabela_dados, nova_linha], ignore_index=True)

# --- EXIBIÇÃO ---
if not st.session_state.tabela_dados.empty:
    st.subheader("Resposta Atual:")
    st.write(st.session_state.tabela_dados.iloc[-1]["Resposta"])
    
    st.divider()
    st.subheader("📊 Histórico de Dados Salvos")
    st.dataframe(st.session_state.tabela_dados, use_container_width=True)
    
    # Exportação
    csv = st.session_state.tabela_dados.to_csv(index=False).encode('utf-8')
    st.download_button("Baixar Dados (CSV)", csv, "historico_ia.csv", "text/csv")
