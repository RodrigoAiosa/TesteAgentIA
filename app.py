import streamlit as st
import requests
import os
import pandas as pd
import time
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Chat IA Pro", page_icon="✍️", layout="wide")

# --- INJEÇÃO DE CSS (FOCO EM LEGIBILIDADE E ESTILO) ---
def apply_custom_style():
    img_url = "https://raw.githubusercontent.com/rodrigoaiosa/TesteAgentIA/main/AIOSA_LOGO.jpg"
    
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=EB+Garamond:wght@500;700&display=swap');

        /* 1. LIMPEZA DA INTERFACE */
        header, footer, #MainMenu {{visibility: hidden !important;}}
        [data-testid="stAppDeployButton"], [data-testid="manage-app-button"], 
        .stDeployButton, ._terminalButton_rix23_138 {{ display: none !important; }}

        .stAppViewMain {{ margin-top: -60px; }}

        /* 2. BACKGROUND */
        .stApp {{
            background-image: url("{img_url}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}

        /* 3. CONTROLE TOTAL DE TEXTO (PRETO ABSOLUTO) */
        h1 {{
            color: #000000 !important;
            font-family: 'EB Garamond', serif;
            font-weight: 700;
        }}

        /* Balões de Chat e Notificações */
        .stChatMessage, [data-testid="stNotification"], .stAlert {{
            background-color: rgba(255, 248, 231, 0.95) !important;
            border: 1px solid #8B4513;
            border-radius: 15px;
        }}

        /* Força texto preto em todos os elementos de texto do chat */
        .stChatMessage .stMarkdown p, 
        .stChatMessage span,
        .stAlert div,
        [data-testid="stNotification"] div {{
            color: #000000 !important;
            font-family: 'EB Garamond', serif;
            font-size: 1.25rem !important;
            font-weight: 500 !important;
        }}

        [data-testid="stChatMessageUser"] {{
            background-color: rgba(210, 180, 140, 1.0) !important;
        }}

        /* 4. CAMPO DE ENTRADA */
        .stChatInputContainer textarea {{
            color: #000000 !important;
            -webkit-text-fill-color: #000000 !important;
        }}
        
        .stChatInputContainer {{
            background-color: rgba(255, 255, 255, 0.8) !important;
            border: 2px solid #8B4513 !important;
        }}

        /* 5. SIDEBAR */
        [data-testid="stSidebar"] {{ background-color: rgba(45, 28, 25, 0.98) !important; }}
        [data-testid="stSidebar"] * {{ color: #D2B48C !important; }}
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

# --- FUNÇÃO DA IA (CONEXÃO SEGURA) ---
def perguntar_ia(historico):
    contexto = historico[-8:] if len(historico) > 8 else historico
    
    # Prioriza o segredo configurado na imagem que você enviou
    HF_TOKEN = st.secrets.get("HF_TOKEN")
    
    if not HF_TOKEN:
        return "⚠️ Erro: O Token (Secrets) não foi detectado pelo sistema."

    API_URL = "https://router.huggingface.co/v1/chat/completions"
    headers = {"Authorization": f"Bearer {HF_TOKEN}", "Content-Type": "application/json"}
    
    payload = {
        "model": "meta-llama/Llama-3.2-3B-Instruct",
        "messages": contexto,
        "max_tokens": 800,
        "temperature": 0.5
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=20)
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            return f"⚠️ Problema técnico (Código {response.status_code})."
    except Exception as e:
        return f"⚠️ Erro de conexão: {str(e)}"

# --- INTERFACE PRINCIPAL ---
st.title("💬 Sou o Alosa, seu assistente virtual...")

# Exibe o histórico de mensagens
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- FLUXO DE CHAT ---
if prompt := st.chat_input("Como posso ajudar?"):
    st.toast("O Alosa está escrevendo...", icon="✍️")
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_res = ""
        
        with st.spinner("Consultando manuscritos..."):
            resposta = perguntar_ia(st.session_state.messages)
        
        # Tratamento visual para mensagens de erro
        if "⚠️" in resposta:
            placeholder.error(resposta)
            full_res = resposta
        else:
            for chunk in resposta.split(" "):
                full_res += chunk + " "
                time.sleep(0.02)
                placeholder.markdown(full_res + "▌")
            placeholder.markdown(full_res)

    # Preservação dos dados na tabela
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
    st.write(f"Interações documentadas: {len(st.session_state.tabela_dados)}")
