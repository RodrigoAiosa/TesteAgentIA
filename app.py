import streamlit as st
import requests
import os
import pandas as pd
import time
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Chat IA Pro", page_icon="✍️", layout="wide")

# --- INJEÇÃO DE CSS (OCULTAÇÃO, BACKGROUND E FONTES MANUSCRITAS) ---
def apply_custom_style():
    img_url = "https://raw.githubusercontent.com/rodrigoaiosa/TesteAgentIA/main/AIOSA_LOGO.jpg"
    
    st.markdown(
        f"""
        <style>
        /* Importando fonte manuscrita do Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400..800;1,400..800&display=swap');

        /* 1. OCULTAÇÃO DE ELEMENTOS DO SISTEMA */
        header, footer, #MainMenu {{visibility: hidden !important;}}
        [data-testid="stAppDeployButton"], [data-testid="manage-app-button"], .stDeployButton,
        ._terminalButton_rix23_138, div[data-testid="stToolbar"] {{ display: none !important; }}

        .stAppViewMain {{ margin-top: -60px; }}

        /* 2. BACKGROUND */
        .stApp {{
            background-image: url("{img_url}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}

        /* 3. TÍTULO E TEXTOS GERAIS */
        h1 {{
            color: #FFFFFF !important;
            text-shadow: 2px 2px 10px rgba(0,0,0,0.9);
            font-family: 'EB Garamond', serif;
        }}

        /* 4. CHAT ESTILIZADO (Efeito Manuscrito nas Mensagens da IA) */
        .stChatMessage {{
            background-color: rgba(255, 248, 231, 0.85) !important; 
            border-radius: 15px;
            border: 1px solid #8B4513;
            margin-bottom: 15px;
            max-width: 85%;
        }}

        [data-testid="stChatMessageUser"] {{
            margin-left: auto !important;
            flex-direction: row-reverse !important;
            background-color: rgba(210, 180, 140, 0.95) !important;
        }}

        /* Fonte elegante para a resposta da IA */
        [data-testid="stChatMessageAssistant"] .stMarkdown p {{
            font-family: 'EB Garamond', serif;
            font-size: 1.2rem !important;
            color: #2D1C19 !important;
            line-height: 1.4;
        }}

        /* 5. SIDEBAR */
        [data-testid="stSidebar"] {{ background-color: rgba(45, 28, 25, 0.98) !important; }}
        [data-testid="stSidebar"] * {{ color: #D2B48C !important; }}

        /* 6. INPUT */
        .stChatInputContainer {{ background-color: rgba(255, 255, 255, 0.15) !important; }}
        </style>
        """,
        unsafe_allow_html=True
    )

apply_custom_style()

# --- INICIALIZAÇÃO DE ESTADOS ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "tabela_dados" not in st.session_state:
    st.session_state.tabela_dados = pd.DataFrame(columns=["Data/Hora", "Pergunta", "Resposta"])

# --- FUNÇÃO DA IA COM JANELA DE MEMÓRIA (Item 1) ---
def perguntar_ia(mensagens_completas):
    # Janela de Memória: Enviamos apenas as últimas 10 mensagens para manter o foco e economizar tokens
    contexto_reduzido = mensagens_completas[-10:] if len(mensagens_completas) > 10 else mensagens_completas
    
    HF_TOKEN = os.getenv("HF_TOKEN")
    API_URL = "https://router.huggingface.co/v1/chat/completions"
    headers = {"Authorization": f"Bearer {HF_TOKEN}", "Content-Type": "application/json"}
    
    payload = {
        "model": "meta-llama/Llama-3.2-3B-Instruct",
        "messages": contexto_reduzido,
        "max_tokens": 800,
        "temperature": 0.6
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        return f"⚠️ Erro na consulta: {response.status_code}"
    except Exception as e:
        return f"⚠️ Erro de conexão: {str(e)}"

# --- INTERFACE PRINCIPAL ---
st.title("💬 Sou o AIosa, seu assistente virtual...")

# Exibição do Histórico
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- INPUT E LÓGICA ---
if prompt := st.chat_input("Escreva sua mensagem aqui..."):
    # Feedback Visual Rápido (Item 4)
    st.toast("O AIosa está redigindo...", icon="✍️")
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""
        
        with st.spinner("Consultando os manuscritos..."):
            resposta_ia = perguntar_ia(st.session_state.messages)
        
        # Efeito de Digitação
        for chunk in resposta_ia.split(" "):
            full_response += chunk + " "
            time.sleep(0.02)
            placeholder.markdown(full_response + "▌")
        placeholder.markdown(full_response)

    # Salvamento e Preservação de Dados
    st.session_state.messages.append({"role": "assistant", "content": full_response})
    
    nova_linha = pd.DataFrame([{
        "Data/Hora": datetime.now().strftime("%H:%M:%S"), 
        "Pergunta": prompt, 
        "Resposta": full_response
    }])
    st.session_state.tabela_dados = pd.concat([st.session_state.tabela_dados, nova_linha], ignore_index=True)

# --- SIDEBAR ---
with st.sidebar:
    st.subheader("📜 Configurações")
    if st.button("Limpar Conversa"):
        st.session_state.messages = []
        st.rerun()
    
    st.divider()
    # Exibição amigável do status (Item 4 alternativo)
    st.write(f"✍️ **Interações documentadas:** {len(st.session_state.tabela_dados)}")
    
    if len(st.session_state.messages) > 10:
        st.info("💡 O assistente está usando uma janela de memória otimizada para manter a performance.")
