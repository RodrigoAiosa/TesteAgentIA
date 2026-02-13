import streamlit as st
import requests
import os
import pandas as pd
import time
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Chat IA Pro", page_icon="✍️", layout="wide")

# --- INJEÇÃO DE CSS (LEGIBILIDADE SUPREMA) ---
def apply_custom_style():
    img_url = "https://raw.githubusercontent.com/rodrigoaiosa/TesteAgentIA/main/AIOSA_LOGO.jpg"
    
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=EB+Garamond:wght@600;800&display=swap');

        /* Ocultar elementos desnecessários */
        header, footer, #MainMenu {{visibility: hidden !important;}}
        [data-testid="stAppDeployButton"], .stDeployButton {{ display: none !important; }}

        /* Background do App */
        .stApp {{
            background-image: url("{img_url}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}

        /* Títulos e Textos em PRETO nítido */
        h1 {{ color: #000000 !important; font-family: 'EB Garamond', serif; font-weight: 800; }}

        /* Balões de Chat - Quase 100% opacos para garantir a leitura */
        .stChatMessage, .stAlert {{
            background-color: rgba(255, 250, 240, 0.98) !important; 
            border: 2px solid #5D4037;
            border-radius: 12px;
            box-shadow: 2px 2px 10px rgba(0,0,0,0.2);
        }}

        .stChatMessage .stMarkdown p, .stChatMessage span, .stAlert div {{
            color: #000000 !important;
            font-family: 'EB Garamond', serif;
            font-size: 1.35rem !important;
            font-weight: 600 !important;
            line-height: 1.3;
        }}

        /* Balão do Usuário mais escuro para diferenciar */
        [data-testid="stChatMessageUser"] {{ background-color: #E0C9A6 !important; }}

        /* Input de texto */
        .stChatInputContainer textarea {{ color: #000000 !important; font-weight: 600 !important; }}
        .stChatInputContainer {{ background-color: rgba(255, 255, 255, 0.95) !important; border: 2px solid #5D4037 !important; }}
        </style>
        """,
        unsafe_allow_html=True
    )

apply_custom_style()

# --- INICIALIZAÇÃO ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- FUNÇÃO DA IA ---
def perguntar_ia(historico):
    try:
        # Pega o token direto das Secrets configuradas
        token = st.secrets["HF_TOKEN"]
    except:
        return "⚠️ Erro: Adicione o segredo 'HF_TOKEN' nas configurações do Streamlit."

    API_URL = "https://router.huggingface.co/v1/chat/completions"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    payload = {
        "model": "meta-llama/Llama-3.2-3B-Instruct",
        "messages": historico[-6:], # Memória curta para rapidez
        "max_tokens": 700,
        "temperature": 0.7
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=25)
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        elif response.status_code == 401:
            return "⚠️ O Token nas Secrets foi invalidado ou expirou. Por favor, gere um novo no Hugging Face."
        else:
            return f"⚠️ Erro {response.status_code} na API do mestre."
    except Exception as e:
        return f"⚠️ Falha técnica: {str(e)}"

# --- INTERFACE ---
st.title("💬 Sou o Alosa, seu assistente virtual...")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Como posso ajudar hoje?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Consultando os arquivos sagrados..."):
            resposta = perguntar_ia(st.session_state.messages)
        
        if "⚠️" in resposta:
            st.error(resposta)
        else:
            placeholder = st.empty()
            full_res = ""
            for chunk in resposta.split(" "):
                full_res += chunk + " "
                time.sleep(0.015)
                placeholder.markdown(full_res + "▌")
            placeholder.markdown(full_res)
            st.session_state.messages.append({"role": "assistant", "content": full_res})
