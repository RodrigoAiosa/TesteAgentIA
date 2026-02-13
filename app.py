import streamlit as st
import requests
import os
import pandas as pd
import time
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Chat IA Pro", page_icon="✍️", layout="wide")

# --- INJEÇÃO DE CSS (REMOÇÃO DE TEXTO DOS ÍCONES E LEGIBILIDADE) ---
def apply_custom_style():
    img_url = "https://raw.githubusercontent.com/rodrigoaiosa/TesteAgentIA/main/AIOSA_LOGO.jpg"
    
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=EB+Garamond:wght@600;800&display=swap');

        /* 1. OCULTAR ELEMENTOS DE SISTEMA */
        header, footer, #MainMenu {{visibility: hidden !important;}}
        [data-testid="stAppDeployButton"], .stDeployButton {{ display: none !important; }}

        /* 2. BACKGROUND */
        .stApp {{
            background-image: url("{img_url}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}

        /* 3. CORREÇÃO DOS ÍCONES (REMOVE "face" E "smart_toy") */
        /* Esconde o texto que vaza dos avatares padrão do Streamlit */
        [data-testid="stChatMessageAvatarContainer"] div {{
            color: transparent !important;
            font-size: 0px !important;
        }}

        /* 4. TEXTO PRETO E BALÕES SÓLIDOS */
        h1 {{ color: #000000 !important; font-family: 'EB Garamond', serif; font-weight: 800; }}

        .stChatMessage {{
            background-color: rgba(255, 250, 240, 0.98) !important; 
            border: 2px solid #5D4037;
            border-radius: 12px;
            margin-bottom: 10px;
        }}

        /* Força texto preto em todas as mensagens */
        .stChatMessage .stMarkdown p, 
        .stChatMessage span,
        .stAlert div {{
            color: #000000 !important;
            font-family: 'EB Garamond', serif;
            font-size: 1.3rem !important;
            font-weight: 600 !important;
        }}

        /* Diferenciação do balão do usuário */
        [data-testid="stChatMessageUser"] {{ 
            background-color: #E0C9A6 !important; 
        }}

        /* 5. CAMPO DE ENTRADA */
        .stChatInputContainer textarea {{ color: #000000 !important; font-weight: 600 !important; }}
        .stChatInputContainer {{ 
            background-color: rgba(255, 255, 255, 0.95) !important; 
            border: 2px solid #5D4037 !important; 
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

apply_custom_style()

# --- INICIALIZAÇÃO ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "tabela_dados" not in st.session_state:
    st.session_state.tabela_dados = pd.DataFrame(columns=["Data/Hora", "Pergunta", "Resposta"])

# --- FUNÇÃO DA IA ---
def perguntar_ia(historico):
    try:
        token = st.secrets["HF_TOKEN"]
    except:
        return "⚠️ Erro: HF_TOKEN não configurado."

    API_URL = "https://router.huggingface.co/v1/chat/completions"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    payload = {
        "model": "meta-llama/Llama-3.2-3B-Instruct",
        "messages": historico[-6:],
        "max_tokens": 800,
        "temperature": 0.7
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=25)
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            return f"⚠️ Erro na consulta (Status {response.status_code})."
    except Exception as e:
        return f"⚠️ Falha técnica: {str(e)}"

# --- INTERFACE ---
st.title("💬 Sou o Alosa, seu assistente virtual...")

# Exibe histórico usando emojis para evitar os textos "face" e "smart_toy"
for msg in st.session_state.messages:
    # Definimos ícones de emoji que não geram texto extra
    icone = "👤" if msg["role"] == "user" else "✍️"
    with st.chat_message(msg["role"], avatar=icone):
        st.markdown(msg["content"])

# --- PROCESSAMENTO ---
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
            for chunk in resposta.split(" "):
                full_res += chunk + " "
                time.sleep(0.015)
                placeholder.markdown(full_res + "▌")
            placeholder.markdown(full_res)

    # Salvamento e preservação de dados
    st.session_state.messages.append({"role": "assistant", "content": full_res})
    nova_linha = pd.DataFrame([{
        "Data/Hora": datetime.now().strftime("%H:%M:%S"), 
        "Pergunta": prompt, 
        "Resposta": full_res
    }])
    st.session_state.tabela_dados = pd.concat([st.session_state.tabela_dados, nova_linha], ignore_index=True)

with st.sidebar:
    st.subheader("📜 Painel")
    if st.button("Limpar Conversa"):
        st.session_state.messages = []
        st.rerun()
    st.write(f"Registros: {len(st.session_state.tabela_dados)}")
