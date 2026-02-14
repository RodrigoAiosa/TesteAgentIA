import streamlit as st
import requests
import pandas as pd
import time
from datetime import datetime, timedelta, timezone

# ---------------------------------------------------
# CONFIGURAÇÃO DA PÁGINA
# ---------------------------------------------------
st.set_page_config(
    page_title="Alosa IA - Rodrigo Aiosa",
    page_icon="💬",
    layout="wide"
)

# ---------------------------------------------------
# CSS GLOBAL (FORÇANDO TEXTO PRETO)
# ---------------------------------------------------
def apply_custom_style():
    st.markdown("""
        <style>
        header, footer, #MainMenu {visibility: hidden;}

        .stApp {
            background-color: #ECE5DD;
        }

        html, body, p, div, span, label,
        h1, h2, h3, h4, h5, h6,
        li, strong, em, small,
        .stMarkdown, .stText,
        .stChatMessageContent,
        textarea, input {
            color: #000000 !important;
        }

        section[data-testid="stSidebar"] * {
            color: #000000 !important;
        }

        textarea::placeholder {
            color: #000000 !important;
            opacity: 1 !important;
        }

        button {
            color: #000000 !important;
        }

        .chat-bubble {
            padding: 12px 14px;
            border-radius: 10px;
            margin: 6px 0;
            max-width: 70%;
            font-size: 1rem;
            line-height: 1.5;
            font-family: Arial, Helvetica, sans-serif;
            box-shadow: 0 1px 1px rgba(0,0,0,0.1);
            color: #000000 !important;
        }

        .assistant-bubble {
            background-color: #FFFFFF;
            border-bottom-left-radius: 2px;
        }

        .user-bubble {
            background-color: #DCF8C6;
            border-bottom-right-radius: 2px;
        }

        .chat-row {
            display: flex;
            flex-direction: column;
            width: 100%;
        }

        .time {
            font-size: 0.7rem;
            color: #000000 !important;
            text-align: right;
            margin-top: 4px;
        }
        </style>
    """, unsafe_allow_html=True)

apply_custom_style()

# ---------------------------------------------------
# HORA BRASIL UTC-3
# ---------------------------------------------------
def hora_brasil():
    brasil_tz = timezone(timedelta(hours=-3))
    return datetime.now(brasil_tz).strftime("%H:%M")

# ---------------------------------------------------
# CONTEXTO DO ASSISTENTE
# ---------------------------------------------------
def carregar_contexto():
    try:
        with open("instrucoes.txt", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "Você é o Alosa, assistente comercial do Rodrigo Aiosa."

# ---------------------------------------------------
# SESSION STATE
# ---------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": carregar_contexto()}
    ]

if "tabela_dados" not in st.session_state:
    st.session_state.tabela_dados = pd.DataFrame(
        columns=["Data/Hora", "Pergunta", "Resposta"]
    )

# ---------------------------------------------------
# FUNÇÃO IA
# ---------------------------------------------------
def perguntar_ia(historico):
    token = st.secrets.get("HF_TOKEN")
    if not token:
        return "⚠️ HF_TOKEN não configurado."

    API_URL = "https://router.huggingface.co/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "meta-llama/Llama-3.2-3B-Instruct",
        "messages": historico,
        "max_tokens": 1200,
        "temperature": 0.7
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        return "⚠️ Erro API."
    except:
        return "⚠️ Erro de conexão."

# ---------------------------------------------------
# TÍTULO
# ---------------------------------------------------
st.title("💬 Alosa — Consultor Estratégico IA")

# ---------------------------------------------------
# CHAT RENDER
# ---------------------------------------------------
for msg in st.session_state.messages:
    if msg["role"] == "system":
        continue

    bubble_class = "assistant-bubble"
    align = "flex-start"

    if msg["role"] == "user":
        bubble_class = "user-bubble"
        align = "flex-end"

    st.markdown(
        f"""
        <div class="chat-row" style="align-items:{align}">
            <div class="chat-bubble {bubble_class}">
                {msg["content"]}
                <div class="time">{hora_brasil()}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

# ---------------------------------------------------
# INPUT
# ---------------------------------------------------
if prompt := st.chat_input("Digite sua mensagem..."):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.spinner("Alosa está digitando..."):
        resposta = perguntar_ia(st.session_state.messages)

    placeholder = st.empty()
    full_res = ""

    for chunk in resposta.split(" "):
        full_res += chunk + " "
        time.sleep(0.015)
        placeholder.markdown(
            f"""
            <div class="chat-row" style="align-items:flex-start">
                <div class="chat-bubble assistant-bubble">
                    {full_res}▌
                    <div class="time">{hora_brasil()}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    placeholder.markdown(
        f"""
        <div class="chat-row" style="align-items:flex-start">
            <div class="chat-bubble assistant-bubble">
                {full_res}
                <div class="time">{hora_brasil()}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.session_state.messages.append(
        {"role": "assistant", "content": full_res}
    )

    nova_linha = pd.DataFrame([{
        "Data/Hora": hora_brasil(),
        "Pergunta": prompt,
        "Resposta": full_res
    }])

    st.session_state.tabela_dados = pd.concat(
        [st.session_state.tabela_dados, nova_linha],
        ignore_index=True
    )

# ---------------------------------------------------
# SIDEBAR
# ---------------------------------------------------
with st.sidebar:
    st.subheader("📜 Painel de Gestão")

    if st.button("Nova Conversa"):
        st.session_state.messages = [
            {"role": "system", "content": carregar_contexto()}
        ]
        st.rerun()

    st.write(f"Interações: {len(st.session_state.tabela_dados)}")

    st.markdown("---")

    wa_link = "https://wa.me/5511977019335?text=Oi,%20Rodrigo!%20Vim%20pelo%20Chat%20IA."
    st.markdown(f"**WhatsApp:** [(11) 97701-9335]({wa_link})")
    st.markdown("**E-mail:** rodrigoaiosa@gmail.com")
