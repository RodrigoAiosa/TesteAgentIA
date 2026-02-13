import streamlit as st
import requests
import os
import pandas as pd
import time
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Chat IA Pro - Rodrigo Aiosa", page_icon="✍️", layout="wide")

# --- INJEÇÃO DE CSS (FOCO EM PRETO ABSOLUTO E ESTILO MANUSCRITO) ---
def apply_custom_style():
    img_url = "https://raw.githubusercontent.com/rodrigoaiosa/TesteAgentIA/main/AIOSA_LOGO.jpg"
    
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=EB+Garamond:wght@600;800&display=swap');

        /* 1. OCULTAR INTERFACE PADRÃO */
        header, footer, #MainMenu {{visibility: hidden !important;}}
        [data-testid="stAppDeployButton"], .stDeployButton {{ display: none !important; }}

        /* 2. BACKGROUND */
        .stApp {{
            background-image: url("{img_url}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}

        /* 3. REMOVER TEXTOS DOS AVATARES */
        [data-testid="stChatMessageAvatarContainer"] div {{
            color: transparent !important;
            font-size: 0px !important;
        }}

        /* 4. TEXTOS EM PRETO ABSOLUTO */
        h1, h2, h3, p, span, li, div {{
            font-family: 'EB Garamond', serif !important;
        }}

        .stChatMessage .stMarkdown p, 
        .stChatMessage .stMarkdown li,
        .stChatMessage span,
        .stAlert div,
        [data-testid="stNotification"] div {{
            color: #000000 !important;
            font-size: 1.35rem !important;
            font-weight: 600 !important;
        }}

        /* 5. BALÕES DE MENSAGEM */
        .stChatMessage {{
            background-color: rgba(255, 250, 240, 0.98) !important; 
            border: 2px solid #5D4037;
            border-radius: 12px;
            margin-bottom: 10px;
        }}

        [data-testid="stChatMessageUser"] {{ 
            background-color: #E0C9A6 !important; 
        }}

        /* 6. CAMPO DE ENTRADA */
        .stChatInputContainer textarea {{ 
            color: #000000 !important; 
            font-weight: 600 !important; 
            -webkit-text-fill-color: #000000 !important;
        }}
        
        .stChatInputContainer {{ 
            background-color: rgba(255, 255, 255, 0.95) !important; 
            border: 2px solid #5D4037 !important; 
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

apply_custom_style()

# --- FUNÇÃO CARREGAR CONHECIMENTO (CÉREBRO TXT) ---
def carregar_contexto():
    try:
        with open("instrucoes.txt", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "Você é o Alosa, assistente do Rodrigo Aiosa."

# --- INICIALIZAÇÃO E MEMÓRIA ---
if "messages" not in st.session_state:
    contexto_inicial = carregar_contexto()
    st.session_state.messages = [{"role": "system", "content": contexto_inicial}]

if "tabela_dados" not in st.session_state:
    st.session_state.tabela_dados = pd.DataFrame(columns=["Data/Hora", "Pergunta", "Resposta"])

# --- FUNÇÃO DA IA ---
def perguntar_ia(historico):
    token = st.secrets.get("HF_TOKEN")
    if not token:
        return "⚠️ Erro: HF_TOKEN não configurado nas Secrets."

    API_URL = "https://router.huggingface.co/v1/chat/completions"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    payload = {
        "model": "meta-llama/Llama-3.2-3B-Instruct",
        "messages": historico, # Envia o histórico com o system prompt
        "max_tokens": 800,
        "temperature": 0.7
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=25)
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            return f"⚠️ Problema na API (Código {response.status_code})."
    except Exception as e:
        return f"⚠️ Erro técnico: {str(e)}"

# --- INTERFACE PRINCIPAL ---
st.title("💬 Sou o Alosa, seu assistente virtual...")

# Exibição do Histórico (Ocultando a instrução de sistema)
for msg in st.session_state.messages:
    if msg["role"] != "system":
        icone = "👤" if msg["role"] == "user" else "✍️"
        with st.chat_message(msg["role"], avatar=icone):
            st.markdown(msg["content"])

# --- PROCESSAMENTO DO PROMPT ---
if prompt := st.chat_input("Como posso ajudar hoje?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="✍️"):
        placeholder = st.empty()
        full_res = ""
        
        with st.spinner("Consultando manuscritos..."):
            resposta = perguntar_ia(st.session_state.messages)
        
        if "⚠️" in resposta:
            st.error(resposta)
            full_res = resposta
        else:
            # Efeito de digitação
            for chunk in resposta.split(" "):
                full_res += chunk + " "
                time.sleep(0.015)
                placeholder.markdown(full_res + "▌")
            placeholder.markdown(full_res)

    # Salvamento e Preservação de Dados
    st.session_state.messages.append({"role": "assistant", "content": full_res})
    nova_linha = pd.DataFrame([{
        "Data/Hora": datetime.now().strftime("%H:%M:%S"), 
        "Pergunta": prompt, 
        "Resposta": full_res
    }])
    st.session_state.tabela_dados = pd.concat([st.session_state.tabela_dados, nova_linha], ignore_index=True)

# --- SIDEBAR ---
with st.sidebar:
    st.subheader("📜 Painel de Controle")
    if st.button("Limpar Conversa"):
        st.session_state.messages = [{"role": "system", "content": carregar_contexto()}]
        st.rerun()
    st.write(f"Interações registradas: {len(st.session_state.tabela_dados)}")
