import streamlit as st
import requests
import os
import pandas as pd
import time
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Chat IA Pro", page_icon="💬", layout="centered")

# Estilo para centralizar o chat e melhorar a aparência
st.markdown("""
    <style>
    .stApp { max-width: 850px; margin: 0 auto; }
    .stChatMessage { border-radius: 15px; }
    </style>
    """, unsafe_allow_html=True)

st.title("💬 Sou o AIosa, seu assistente virtual...")

# --- CONFIGURAÇÕES DE API ---
HF_TOKEN = os.getenv("HF_TOKEN")
API_URL = "https://router.huggingface.co/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {HF_TOKEN}",
    "Content-Type": "application/json",
}

# --- INICIALIZAÇÃO DE ESTADOS (Preservando dados) ---
if "messages" not in st.session_state:
    st.session_state.messages = []

if "tabela_dados" not in st.session_state:
    # Mantendo a estrutura para salvar novos dados e preservar existentes
    st.session_state.tabela_dados = pd.DataFrame(columns=["Data/Hora", "Pergunta", "Resposta"])

def perguntar_ia(mensagens_historico):
    payload = {
        "model": "meta-llama/Llama-3.2-3B-Instruct",
        "messages": mensagens_historico,
        "max_tokens": 600,
        "temperature": 0.7,
        "stream": False # O streaming visual será simulado para maior estabilidade no Streamlit
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            return f"⚠️ Erro: {response.status_code}"
    except Exception as e:
        return f"⚠️ Erro de conexão: {str(e)}"

# --- EXIBIÇÃO DO HISTÓRICO VISUAL ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- INPUT E LÓGICA DE CHAT ---
if prompt := st.chat_input("Como posso ajudar?"):
    
    # 1. Exibe e guarda mensagem do usuário
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Resposta da IA com efeito de escrita (Streaming)
    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""
        
        with st.spinner("Pensando..."):
            resposta_bruta = perguntar_ia(st.session_state.messages)
        
        # Simulação do efeito de digitação
        for chunk in resposta_bruta.split(" "):
            full_response += chunk + " "
            time.sleep(0.05)
            placeholder.markdown(full_response + "▌")
        placeholder.markdown(full_response)

    # 3. Salvamento silencioso dos dados (Sempre preservando o histórico)
    st.session_state.messages.append({"role": "assistant", "content": full_response})
    
    nova_linha = pd.DataFrame([{
        "Data/Hora": datetime.now().strftime("%H:%M:%S"),
        "Pergunta": prompt,
        "Resposta": full_response
    }])
    st.session_state.tabela_dados = pd.concat([st.session_state.tabela_dados, nova_linha], ignore_index=True)

# --- MENU LATERAL (Opcional) ---
with st.sidebar:
    st.subheader("Configurações")
    if st.button("Limpar Chat"):
        st.session_state.messages = []
        st.rerun()
    
    st.divider()
    # Apenas um indicador de que os dados estão sendo salvos conforme solicitado
    st.caption(f"Interações salvas nesta sessão: {len(st.session_state.tabela_dados)}")
