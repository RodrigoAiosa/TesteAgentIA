import streamlit as st
import requests
import os
import pandas as pd
import time
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Chat IA Pro", page_icon="💬", layout="wide")

# --- INJEÇÃO DE CSS REFORÇADO PARA OCULTAÇÃO TOTAL ---
def apply_custom_style():
    # Link direto da imagem
    img_url = "https://raw.githubusercontent.com/rodrigoaiosa/TesteAgentIA/main/AIOSA_LOGO.jpg"
    
    st.markdown(
        f"""
        <style>
        /* 1. REMOÇÃO AGRESSIVA DE INTERFACE ADMINISTRATIVA */
        #MainMenu {{visibility: hidden !important;}}
        footer {{visibility: hidden !important;}}
        header {{visibility: hidden !important;}}
        
        /* Oculta botões de deploy e o persistente 'Manage app' */
        .stDeployButton {{display:none !important;}}
        [data-testid="stAppDeployButton"] {{display:none !important;}}
        [data-testid="stToolbar"] {{display:none !important;}}
        [data-testid="stDecoration"] {{display:none !important;}}
        
        /* Alvo específico para o botão de host do Streamlit Cloud */
        [data-testid="manage-app-button"], 
        .st-emotion-cache-zq5wmm, 
        button[title="Manage app"] {{
            display: none !important;
            visibility: hidden !important;
        }}

        /* 2. BACKGROUND AJUSTADO */
        .stApp {{
            background-image: url("{img_url}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}

        /* 3. TÍTULO EM BRANCO */
        h1 {{
            color: #FFFFFF !important;
            text-shadow: 2px 2px 10px rgba(0,0,0,0.9);
            font-family: 'serif';
            font-weight: bold;
        }}

        /* 4. CHAT ALTERNADO (USUÁRIO À DIREITA, IA À ESQUERDA) */
        .stChatMessage {{
            background-color: rgba(255, 248, 231, 0.8) !important; 
            border-radius: 15px;
            border: 1px solid #8B4513;
            margin-bottom: 15px;
            max-width: 80%;
            display: flex !important;
        }}

        /* Alinhamento Usuário */
        [data-testid="stChatMessageUser"] {{
            margin-left: auto !important;
            flex-direction: row-reverse !important;
            background-color: rgba(210, 180, 140, 0.9) !important;
        }}

        /* Alinhamento Assistente */
        [data-testid="stChatMessageAssistant"] {{
            margin-right: auto !important;
        }}

        /* Texto em PRETO no chat */
        .stChatMessage .stMarkdown p {{
            color: #000000 !important;
            font-weight: 500;
        }}

        /* 5. SIDEBAR MARROM */
        [data-testid="stSidebar"] {{
            background-color: rgba(45, 28, 25, 0.98) !important; 
        }}
        [data-testid="stSidebar"] .stMarkdown p, 
        [data-testid="stSidebar"] h3 {{
            color: #D2B48C !important;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

apply_custom_style()

st.title("💬 Sou o AIosa, seu assistente virtual...")

# --- CONFIGURAÇÕES DE API ---
HF_TOKEN = os.getenv("HF_TOKEN")
API_URL = "https://router.huggingface.co/v1/chat/completions"
headers = { "Authorization": f"Bearer {HF_TOKEN}", "Content-Type": "application/json" }

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
        return response.json()["choices"][0]["message"]["content"] if response.status_code == 200 else f"⚠️ Erro: {response.status_code}"
    except Exception as e:
        return f"⚠️ Erro de conexão: {str(e)}"

# --- EXIBIÇÃO DO HISTÓRICO VISUAL ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- INPUT E LÓGICA DE CHAT ---
if prompt := st.chat_input("Como posso ajudar?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""
        with st.spinner("Lendo manuscritos..."):
            resposta_bruta = perguntar_ia(st.session_state.messages)
        
        for chunk in resposta_bruta.split(" "):
            full_response += chunk + " "
            time.sleep(0.04)
            placeholder.markdown(full_response + "▌")
        placeholder.markdown(full_response)

    # Salvamento de dados e preservação de histórico conforme instrução
    st.session_state.messages.append({"role": "assistant", "content": full_response})
    nova_linha = pd.DataFrame([{"Data/Hora": datetime.now().strftime("%H:%M:%S"), "Pergunta": prompt, "Resposta": full_response}])
    st.session_state.tabela_dados = pd.concat([st.session_state.tabela_dados, nova_linha], ignore_index=True)

# --- MENU LATERAL ---
with st.sidebar:
    st.subheader("Configurações")
    if st.button("Limpar Chat"):
        st.session_state.messages = []
        st.rerun()
    st.divider()
    st.caption(f"Interações documentadas: {len(st.session_state.tabela_dados)}")
