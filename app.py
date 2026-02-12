import streamlit as st
import requests
import os
import pandas as pd
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Assistente IA Pro", page_icon="🤖", layout="wide")
st.title("🤖 Assistente IA Online")

# --- CONFIGURAÇÕES DE API ---
HF_TOKEN = os.getenv("HF_TOKEN")
# URL obrigatória conforme o erro 410 anterior
API_URL = "https://router.huggingface.co/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {HF_TOKEN}",
    "Content-Type": "application/json",
}

# --- PERSISTÊNCIA DE DADOS ---
if "tabela_dados" not in st.session_state:
    st.session_state.tabela_dados = pd.DataFrame(columns=["Data/Hora", "Pergunta", "Resposta"])

def perguntar_ia(pergunta):
    # Usando Llama-3.2 que é um Chat Model nativo para evitar o Erro 400
    payload = {
        "model": "meta-llama/Llama-3.2-3B-Instruct",
        "messages": [
            {"role": "system", "content": "Você é um assistente útil e conciso."},
            {"role": "user", "content": pergunta}
        ],
        "max_tokens": 500,
        "temperature": 0.7
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            return data["choices"][0]["message"]["content"]
        else:
            return f"Erro {response.status_code}: {response.text}"
    except Exception as e:
        return f"Erro de conexão: {str(e)}"

# --- INTERFACE ---
with st.container():
    pergunta_usuario = st.text_input("Digite sua pergunta:", key="input_user")
    btn_enviar = st.button("Enviar")

if btn_enviar and pergunta_usuario:
    with st.spinner("Consultando IA..."):
        resposta_ia = perguntar_ia(pergunta_usuario)
        
        # Criar nova linha para a tabela
        nova_linha = pd.DataFrame([{
            "Data/Hora": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "Pergunta": pergunta_usuario,
            "Resposta": resposta_ia
        }])
        
        # Adicionar à tabela existente na sessão (Preservando dados)
        st.session_state.tabela_dados = pd.concat([st.session_state.tabela_dados, nova_linha], ignore_index=True)

# --- EXIBIÇÃO DO HISTÓRICO ---
if not st.session_state.tabela_dados.empty:
    st.markdown("### Resposta Atual:")
    st.info(st.session_state.tabela_dados.iloc[-1]["Resposta"])
    
    st.divider()
    st.subheader("📊 Histórico de Dados Salvos")
    st.dataframe(st.session_state.tabela_dados, use_container_width=True)
    
    # Botão de download do histórico acumulado
    csv = st.session_state.tabela_dados.to_csv(index=False).encode('utf-8')
    st.download_button("Baixar Dados (CSV)", csv, "historico_ia.csv", "text/csv")
