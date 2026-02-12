import streamlit as st
import requests
import os
import pandas as pd
import time
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Chat IA Pro", page_icon="💬", layout="centered")

# --- ESTILIZAÇÃO CUSTOMIZADA (Paleta de Cores da Imagem) ---
def add_bg_and_style():
    st.markdown(
        f"""
        <style>
        /* Fundo da tela principal */
        .stApp {{
            background-image: url("https://raw.githubusercontent.com/seu-usuario/seu-repositorio/main/AIOSA_LOGO.jpg");
            background-attachment: fixed;
            background-size: cover;
        }}

        /* Centralização e largura do chat */
        .stMain {{
            max-width: 850px;
            margin: 0 auto;
        }}

        /* Estilização das mensagens do usuário */
        [data-testid="stChatMessage"]:nth-child(even) {{
            background-color: rgba(210, 180, 140, 0.8) !important; /* Sépia claro */
            border: 1px solid #8B4513;
            color: #3E2723;
        }}

        /* Estilização das mensagens do assistente */
        [data-testid="stChatMessage"]:nth-child(odd) {{
            background-color: rgba(245, 245, 220, 0.9) !important; /* Bege pergaminho */
            border: 1px solid #A0522D;
            color: #3E2723;
        }}

        /* Estilização da Sidebar (Barra Lateral) */
        [data-testid="stSidebar"] {{
            background-color: rgba(62, 39, 35, 0.9) !important; /* Marrom escuro */
        }}
        [data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] p {{
            color: #D2B48C !important;
        }}

        /* Títulos e Textos */
        h1 {{
            color: #3E2723 !important;
            text-shadow: 1px 1px 2px rgba(255,255,255,0.5);
        }}

        /* Input de texto */
        .stChatInputContainer {{
            background-color: rgba(255, 255, 255, 0.2) !important;
            border-radius: 10px;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

add_bg_and_style()

# Nota: Certifique-se de substituir o link da imagem acima pelo link "Raw" correto do seu GitHub.

st.title("💬 Sou o AIosa, seu assistente virtual...")

# --- CONFIGURAÇÕES DE API ---
HF_TOKEN = os.getenv("HF_TOKEN")
API_URL = "https://router.huggingface.co/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {HF_TOKEN}",
    "Content-Type": "application/json",
}

# --- INICIALIZAÇÃO DE ESTADOS (Preservando dados conforme solicitado) ---
if "messages" not in st.session_state:
    st.session_state.messages = []

if "tabela_dados" not in st.session_state:
    st.session_state.tabela_dados = pd.DataFrame(columns=["Data/Hora", "Pergunta", "Resposta"])

def perguntar_ia(mensagens_historico):
    payload = {
        "model": "meta-llama/Llama-3.2-3B-Instruct",
        "messages": mensagens_historico,
        "max_tokens": 600,
        "temperature": 0.7,
        "stream": False 
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

    # 2. Resposta da IA com efeito de escrita
    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""
        
        with st.spinner("Pensando..."):
            resposta_bruta = perguntar_ia(st.session_state.messages)
        
        for chunk in resposta_bruta.split(" "):
            full_response += chunk + " "
            time.sleep(0.05)
            placeholder.markdown(full_response + "▌")
        placeholder.markdown(full_response)

    # 3. Salvamento silencioso e preservação de dados
    st.session_state.messages.append({"role": "assistant", "content": full_response})
    
    nova_linha = pd.DataFrame([{
        "Data/Hora": datetime.now().strftime("%H:%M:%S"),
        "Pergunta": prompt,
        "Resposta": full_response
    }])
    st.session_state.tabela_dados = pd.concat([st.session_state.tabela_dados, nova_linha], ignore_index=True)

# --- MENU LATERAL ---
with st.sidebar:
    st.subheader("Configurações")
    if st.button("Limpar Chat"):
        st.session_state.messages = []
        st.rerun()
    
    st.divider()
    st.caption(f"Interações salvas nesta sessão: {len(st.session_state.tabela_dados)}")
