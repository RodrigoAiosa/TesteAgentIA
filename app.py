import streamlit as st
import requests
import os
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Chat IA", page_icon="💬", layout="centered")

# CSS personalizado para remover o excesso de margens e melhorar o visual
st.markdown("""
    <style>
    .stApp { max-width: 800px; margin: 0 auto; }
    .stChatMessage { border-radius: 15px; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("💬 Minha IA Assistente")

# --- CONFIGURAÇÕES DE API ---
HF_TOKEN = os.getenv("HF_TOKEN")
API_URL = "https://router.huggingface.co/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {HF_TOKEN}",
    "Content-Type": "application/json",
}

# --- HISTÓRICO DA CONVERSA (Design ChatGPT) ---
# Inicializa a lista de mensagens se não existir
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Olá! Como posso te ajudar hoje?"}
    ]

def perguntar_ia(mensagens_historico):
    """Envia o histórico completo para a IA manter o contexto"""
    payload = {
        "model": "meta-llama/Llama-3.2-3B-Instruct",
        "messages": mensagens_historico,
        "max_tokens": 500,
        "temperature": 0.7
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        if response.status_code == 200:
            data = response.json()
            return data["choices"][0]["message"]["content"]
        else:
            return f"⚠️ Erro na API: {response.status_code}"
    except Exception as e:
        return f"⚠️ Erro de conexão: {str(e)}"

# --- EXIBIÇÃO DO CHAT ---
# Renderiza todas as mensagens do histórico na tela
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- CAMPO DE ENTRADA (Chat Input estilo ChatGPT) ---
if prompt := st.chat_input("Digite sua mensagem..."):
    
    # 1. Adiciona e exibe a mensagem do usuário
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Gera e exibe a resposta da IA
    with st.chat_message("assistant"):
        with st.spinner("Digitando..."):
            # Enviamos o histórico completo para a IA ter memória da conversa
            resposta = perguntar_ia(st.session_state.messages)
            st.markdown(resposta)
            
    # 3. Adiciona a resposta ao histórico para a próxima interação
    st.session_state.messages.append({"role": "assistant", "content": resposta})

# Botão opcional no menu lateral para resetar a conversa
with st.sidebar:
    if st.button("Limpar Conversa"):
        st.session_state.messages = [{"role": "assistant", "content": "Olá! Como posso te ajudar hoje?"}]
        st.rerun()
