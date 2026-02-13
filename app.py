import streamlit as st
import requests
import os
import pandas as pd
import time
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Chat IA Pro", page_icon="✍️", layout="wide")

# --- INJEÇÃO DE CSS (FOCO EM TEXTO PRETO E LEGIBILIDADE) ---
def apply_custom_style():
    img_url = "https://raw.githubusercontent.com/rodrigoaiosa/TesteAgentIA/main/AIOSA_LOGO.jpg"
    
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=EB+Garamond:wght@400;700&display=swap');

        /* 1. OCULTAÇÃO DE INTERFACE DE SISTEMA */
        header, footer, #MainMenu {{visibility: hidden !important;}}
        [data-testid="stAppDeployButton"], [data-testid="manage-app-button"], 
        .stDeployButton, ._terminalButton_rix23_138 {{ display: none !important; }}

        /* 2. BACKGROUND */
        .stApp {{
            background-image: url("{img_url}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}

        /* 3. TEXTOS EM PRETO (FORÇADO) */
        /* Título Principal */
        h1 {{
            color: #000000 !important;
            font-family: 'EB Garamond', serif;
            font-weight: 700;
            text-shadow: none !important; /* Removido shadow para clareza */
        }}

        /* Mensagens do Chat */
        .stChatMessage {{
            background-color: rgba(255, 248, 231, 0.9) !important; 
            border: 1px solid #8B4513;
            border-radius: 15px;
        }}

        /* Força a cor PRETA em todos os parágrafos e textos do chat */
        .stChatMessage .stMarkdown p, 
        .stChatMessage [data-testid="stMarkdownContainer"] p,
        .stChatMessage span {{
            color: #000000 !important;
            font-family: 'EB Garamond', serif;
            font-size: 1.25rem !important;
            font-weight: 500 !important;
        }}

        /* Balão do Usuário (Diferenciação leve no fundo, mas texto preto) */
        [data-testid="stChatMessageUser"] {{
            background-color: rgba(210, 180, 140, 0.95) !important;
        }}

        /* 4. CAMPO DE ENTRADA (INPUT) */
        /* Força o texto digitado a ser preto e visível */
        .stChatInputContainer textarea {{
            color: #000000 !important;
            -webkit-text-fill-color: #000000 !important;
        }}
        
        .stChatInputContainer {{
            background-color: rgba(255, 255, 255, 0.6) !important;
            border: 1px solid #8B4513 !important;
        }}

        /* 5. SIDEBAR */
        [data-testid="stSidebar"] {{ background-color: rgba(45, 28, 25, 0.98) !important; }}
        [data-testid="stSidebar"] * {{ color: #D2B48C !important; }}
        </style>
        """,
        unsafe_allow_html=True
    )

apply_custom_style()

# --- INICIALIZAÇÃO E MEMÓRIA ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "tabela_dados" not in st.session_state:
    st.session_state.tabela_dados = pd.DataFrame(columns=["Data/Hora", "Pergunta", "Resposta"])

# --- FUNÇÃO DA IA (MEMÓRIA DE CURTO PRAZO) ---
def perguntar_ia(historico):
    # Janela de memória: enviamos apenas as últimas 8 interações
    contexto = historico[-8:] if len(historico) > 8 else historico
    
    HF_TOKEN = os.getenv("HF_TOKEN")
    API_URL = "https://router.huggingface.co/v1/chat/completions"
    headers = {"Authorization": f"Bearer {HF_TOKEN}", "Content-Type": "application/json"}
    
    payload = {
        "model": "meta-llama/Llama-3.2-3B-Instruct",
        "messages": contexto,
        "max_tokens": 800,
        "temperature": 0.5
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        return response.json()["choices"][0]["message"]["content"]
    except:
        return "⚠️ Ocorreu um erro ao redigir a resposta."

# --- INTERFACE ---
st.title("💬 Sou o AIosa, seu assistente virtual...")

# Exibe histórico com os novos estilos
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- PROCESSAMENTO ---
if prompt := st.chat_input("Escreva sua dúvida aqui..."):
    # Notificação Toast
    st.toast("O AIosa está redigindo...", icon="✍️")
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_res = ""
        
        with st.spinner("Consultando arquivos..."):
            resposta = perguntar_ia(st.session_state.messages)
        
        for chunk in resposta.split(" "):
            full_res += chunk + " "
            time.sleep(0.02)
            placeholder.markdown(full_res + "▌")
        placeholder.markdown(full_res)

    # Salvamento e Preservação
    st.session_state.messages.append({"role": "assistant", "content": full_res})
    nova_linha = pd.DataFrame([{
        "Data/Hora": datetime.now().strftime("%H:%M:%S"), 
        "Pergunta": prompt, 
        "Resposta": full_res
    }])
    st.session_state.tabela_dados = pd.concat([st.session_state.tabela_dados, nova_linha], ignore_index=True)

# --- SIDEBAR ---
with st.sidebar:
    st.subheader("📜 Painel")
    if st.button("Limpar Histórico"):
        st.session_state.messages = []
        st.rerun()
    st.divider()
    st.write(f"Interações: {len(st.session_state.tabela_dados)}")
