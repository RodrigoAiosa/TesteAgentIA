import streamlit as st
import requests
import os
import pandas as pd
import time
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Chat IA Pro", page_icon="✍️", layout="wide")

# --- INJEÇÃO DE CSS (LEGIBILIDADE TOTAL) ---
def apply_custom_style():
    img_url = "https://raw.githubusercontent.com/rodrigoaiosa/TesteAgentIA/main/AIOSA_LOGO.jpg"
    
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=EB+Garamond:wght@500;700&display=swap');

        /* 1. LIMPEZA E BACKGROUND */
        header, footer, #MainMenu {{visibility: hidden !important;}}
        [data-testid="stAppDeployButton"], [data-testid="manage-app-button"], 
        .stDeployButton, ._terminalButton_rix23_138 {{ display: none !important; }}

        .stApp {{
            background-image: url("{img_url}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}

        /* 2. TEXTO PRETO E BALÕES SÓLIDOS */
        h1 {{ color: #000000 !important; font-family: 'EB Garamond', serif; }}

        .stChatMessage, .stAlert {{
            background-color: rgba(255, 248, 231, 0.98) !important; 
            border: 1px solid #8B4513;
            border-radius: 15px;
        }}

        .stChatMessage .stMarkdown p, .stChatMessage span, .stAlert div {{
            color: #000000 !important;
            font-family: 'EB Garamond', serif;
            font-size: 1.3rem !important;
            font-weight: 500 !important;
        }}

        [data-testid="stChatMessageUser"] {{ background-color: rgba(210, 180, 140, 1.0) !important; }}

        /* 3. INPUT CLARO */
        .stChatInputContainer textarea {{ color: #000000 !important; }}
        .stChatInputContainer {{ background-color: rgba(255, 255, 255, 0.9) !important; }}
        </style>
        """,
        unsafe_allow_html=True
    )

apply_custom_style()

# --- INICIALIZAÇÃO ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- FUNÇÃO DA IA (COM DIAGNÓSTICO DE TOKEN) ---
def perguntar_ia(historico):
    # Tenta ler das Secrets (conforme sua configuração na imagem 87499c)
    try:
        token = st.secrets["HF_TOKEN"]
    except:
        return "⚠️ Erro: HF_TOKEN não encontrado nas Secrets do Streamlit."

    API_URL = "https://router.huggingface.co/v1/chat/completions"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    payload = {
        "model": "meta-llama/Llama-3.2-3B-Instruct",
        "messages": historico[-8:], 
        "max_tokens": 800
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=20)
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        elif response.status_code == 401:
            return "⚠️ Erro 401: O Token nas Secrets é inválido. Gere um novo token 'Read' no Hugging Face."
        else:
            return f"⚠️ Erro {response.status_code}: {response.text[:100]}"
    except Exception as e:
        return f"⚠️ Falha de conexão: {str(e)}"

# --- INTERFACE ---
st.title("💬 Sou o Alosa, seu assistente virtual...")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Como posso ajudar?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Consultando manuscritos..."):
            resposta = perguntar_ia(st.session_state.messages)
        
        if "⚠️" in resposta:
            st.error(resposta)
        else:
            placeholder = st.empty()
            full_res = ""
            for chunk in resposta.split(" "):
                full_res += chunk + " "
                time.sleep(0.02)
                placeholder.markdown(full_res + "▌")
            placeholder.markdown(full_res)
            st.session_state.messages.append({"role": "assistant", "content": full_res})
