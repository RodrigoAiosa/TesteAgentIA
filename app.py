import streamlit as st
import requests
import os
import pandas as pd
import time
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Alosa IA - Rodrigo Aiosa", page_icon="💬", layout="wide")

# --- INJEÇÃO DE CSS ESTILO WHATSAPP ---
def apply_whatsapp_style():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Segoe+UI:wght@400;600&display=swap');
        
        /* Ocultar elementos do Streamlit */
        header, footer, #MainMenu {visibility: hidden !important;}
        [data-testid="stAppDeployButton"] { display: none !important; }
        
        /* Fundo padrão WhatsApp */
        .stApp {
            background-color: #E5DDD5;
            background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 100 100"><rect fill="%23E5DDD5" width="100" height="100"/><circle fill="%23D9D3CC" opacity="0.4" cx="25" cy="25" r="15"/><circle fill="%23D9D3CC" opacity="0.3" cx="75" cy="75" r="20"/><circle fill="%23D9D3CC" opacity="0.35" cx="60" cy="30" r="12"/></svg>');
        }

        /* Fonte padrão */
        * {
            font-family: 'Segoe UI', Helvetica, Arial, sans-serif !important;
        }

        /* Container de mensagens */
        .stChatMessage {
            border-radius: 7.5px !important;
            padding: 6px 7px 8px 9px !important;
            margin: 4px 0 !important;
            max-width: 65% !important;
            box-shadow: 0 1px 0.5px rgba(0,0,0,0.13) !important;
            position: relative !important;
        }

        /* Mensagem do usuário (esquerda - branco) */
        [data-testid="stChatMessageUser"] {
            background-color: #FFFFFF !important;
            margin-right: auto !important;
            margin-left: 8px !important;
        }

        [data-testid="stChatMessageUser"]::before {
            content: '';
            position: absolute;
            left: -8px;
            top: 0;
            width: 0;
            height: 0;
            border-style: solid;
            border-width: 0 8px 13px 0;
            border-color: transparent #FFFFFF transparent transparent;
        }

        /* Mensagem do assistente (direita - verde) */
        [data-testid="stChatMessageAssistant"] {
            background-color: #D9FDD3 !important;
            margin-left: auto !important;
            margin-right: 8px !important;
        }

        [data-testid="stChatMessageAssistant"]::after {
            content: '';
            position: absolute;
            right: -8px;
            top: 0;
            width: 0;
            height: 0;
            border-style: solid;
            border-width: 0 0 13px 8px;
            border-color: transparent transparent transparent #D9FDD3;
        }

        /* Texto das mensagens */
        .stChatMessage .stMarkdown p {
            color: #000000 !important;
            font-size: 14.2px !important;
            line-height: 19px !important;
            margin: 0 !important;
            font-weight: 400 !important;
        }

        .stChatMessage .stMarkdown strong {
            font-weight: 600 !important;
        }

        /* Links estilo WhatsApp */
        .stChatMessage a {
            color: #039BE5 !important;
            text-decoration: none !important;
        }

        .stChatMessage a:hover {
            text-decoration: underline !important;
        }

        /* Título */
        h1 {
            color: #075E54 !important;
            font-size: 24px !important;
            font-weight: 600 !important;
            padding: 15px 0 !important;
            text-align: center !important;
            background-color: #075E54 !important;
            color: white !important;
            margin: -1rem -1rem 1rem -1rem !important;
            border-radius: 0 !important;
        }

        /* Input de chat */
        .stChatInputContainer {
            background-color: #F0F0F0 !important;
            border-top: 1px solid #D1D1D1 !important;
            padding: 10px !important;
        }

        .stChatInputContainer textarea {
            background-color: #FFFFFF !important;
            border: 1px solid #D1D1D1 !important;
            border-radius: 21px !important;
            padding: 9px 12px !important;
            color: #000000 !important;
            font-size: 15px !important;
        }

        .stChatInputContainer textarea:focus {
            border-color: #075E54 !important;
            box-shadow: none !important;
        }

        /* Sidebar estilo WhatsApp */
        [data-testid="stSidebar"] {
            background-color: #FFFFFF !important;
            border-right: 1px solid #D1D1D1 !important;
        }

        [data-testid="stSidebar"] h2 {
            color: #075E54 !important;
            font-size: 18px !important;
            font-weight: 600 !important;
        }

        [data-testid="stSidebar"] button {
            background-color: #25D366 !important;
            color: white !important;
            border: none !important;
            border-radius: 5px !important;
            font-weight: 600 !important;
        }

        [data-testid="stSidebar"] button:hover {
            background-color: #1EBE57 !important;
        }

        /* Horário nas mensagens */
        .message-time {
            font-size: 11px !important;
            color: #667781 !important;
            margin-top: 4px !important;
            text-align: right !important;
            display: block !important;
            font-weight: 400 !important;
        }
        
        .message-date {
            font-size: 11px !important;
            color: #8696A0 !important;
            background-color: rgba(255,255,255,0.95) !important;
            padding: 5px 12px !important;
            border-radius: 7.5px !important;
            display: inline-block !important;
            margin: 10px auto !important;
            text-align: center !important;
            box-shadow: 0 1px 0.5px rgba(0,0,0,0.13) !important;
        }

        /* Avatar circular estilo WhatsApp */
        [data-testid="stChatMessageAvatarUser"],
        [data-testid="stChatMessageAvatarAssistant"] {
            border-radius: 50% !important;
            width: 40px !important;
            height: 40px !important;
        }

        /* Spinner */
        .stSpinner > div {
            border-top-color: #25D366 !important;
        }
        </style>
    """, unsafe_allow_html=True)

apply_whatsapp_style()

# --- CARREGAR CONHECIMENTO ---
def carregar_contexto():
    try:
        with open("instrucoes.txt", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "Você é o Alosa, assistente comercial do Rodrigo Aiosa."

# --- INICIALIZAÇÃO ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": carregar_contexto()}]

if "message_timestamps" not in st.session_state:
    st.session_state.message_timestamps = []

if "tabela_dados" not in st.session_state:
    st.session_state.tabela_dados = pd.DataFrame(columns=["Data/Hora", "Pergunta", "Resposta"])

# --- INTEGRAÇÃO COM IA ---
def perguntar_ia(historico):
    token = st.secrets.get("HF_TOKEN")
    if not token: return "⚠️ HF_TOKEN não configurado."
    API_URL = "https://router.huggingface.co/v1/chat/completions"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    payload = {"model": "meta-llama/Llama-3.2-3B-Instruct", "messages": historico, "max_tokens": 1200, "temperature": 0.7}
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
        return response.json()["choices"][0]["message"]["content"] if response.status_code == 200 else "⚠️ Erro API."
    except Exception: return "⚠️ Erro de conexão."

# --- INTERFACE ---
st.title("💬 Alosa IA")

# Mostrar separador de data quando necessário
current_date = None

for idx, msg in enumerate(st.session_state.messages):
    if msg["role"] != "system":
        # Obter timestamp da mensagem
        if idx - 1 < len(st.session_state.message_timestamps):
            msg_datetime = st.session_state.message_timestamps[idx - 1]
        else:
            msg_datetime = datetime.now()
        
        msg_date = msg_datetime.strftime("%d/%m/%Y")
        msg_time = msg_datetime.strftime("%H:%M")
        
        # Mostrar separador de data se mudou o dia
        if msg_date != current_date:
            current_date = msg_date
            st.markdown(f'<div style="text-align: center; margin: 20px 0;"><span class="message-date">{msg_date}</span></div>', unsafe_allow_html=True)
        
        with st.chat_message(msg["role"], avatar="👤" if msg["role"] == "user" else "🤖"):
            st.markdown(msg["content"])
            st.markdown(f'<div class="message-time">{msg_time}</div>', unsafe_allow_html=True)

if prompt := st.chat_input("Digite uma mensagem..."):
    now = datetime.now()
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.message_timestamps.append(now)
    
    msg_date = now.strftime("%d/%m/%Y")
    msg_time = now.strftime("%H:%M")
    
    # Mostrar separador de data se necessário
    if current_date != msg_date:
        st.markdown(f'<div style="text-align: center; margin: 20px 0;"><span class="message-date">{msg_date}</span></div>', unsafe_allow_html=True)
    
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)
        st.markdown(f'<div class="message-time">{msg_time}</div>', unsafe_allow_html=True)

    with st.chat_message("assistant", avatar="🤖"):
        placeholder = st.empty()
        with st.spinner("Digitando..."):
            resposta = perguntar_ia(st.session_state.messages)
        
        full_res = ""
        for chunk in resposta.split(" "):
            full_res += chunk + " "
            time.sleep(0.01)
            placeholder.markdown(full_res + "▌")
        placeholder.markdown(full_res)
        
        now_assistant = datetime.now()
        msg_time_assistant = now_assistant.strftime("%H:%M")
        st.markdown(f'<div class="message-time">{msg_time_assistant}</div>', unsafe_allow_html=True)

    st.session_state.messages.append({"role": "assistant", "content": full_res})
    st.session_state.message_timestamps.append(now_assistant)
    
    # SALVAR E PRESERVAR DADOS
    nova_linha = pd.DataFrame([{"Data/Hora": now.strftime("%d/%m/%Y %H:%M:%S"), "Pergunta": prompt, "Resposta": full_res}])
    st.session_state.tabela_dados = pd.concat([st.session_state.tabela_dados, nova_linha], ignore_index=True)

# --- SIDEBAR ---
with st.sidebar:
    st.subheader("⚙️ Configurações")
    
    if st.button("🔄 Nova Conversa", use_container_width=True):
        st.session_state.messages = [{"role": "system", "content": carregar_contexto()}]
        st.session_state.message_timestamps = []
        st.rerun()
    
    st.write(f"📊 Interações: **{len(st.session_state.tabela_dados)}**")
    
    st.markdown("---")
    st.markdown("### 📞 Contato")
    
    wa_link = "https://wa.me/5511977019335?text=Oi,%20Rodrigo!%20Vim%20pelo%20Chat%20IA."
    st.markdown(f"""
    <div style='background-color: #25D366; padding: 10px; border-radius: 8px; text-align: center; margin-bottom: 10px;'>
        <a href='{wa_link}' target='_blank' style='color: white; text-decoration: none; font-weight: 600;'>
            💬 WhatsApp: (11) 97701-9335
        </a>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div style='background-color: #F0F0F0; padding: 10px; border-radius: 8px; text-align: center;'>
        <a href='mailto:rodrigoaiosa@gmail.com' style='color: #075E54; text-decoration: none; font-weight: 600;'>
            📧 rodrigoaiosa@gmail.com
        </a>
    </div>
    """, unsafe_allow_html=True)
