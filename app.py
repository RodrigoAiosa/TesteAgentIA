import streamlit as st
import requests
import time
from datetime import datetime, timedelta, timezone

# ---------------------------------------------------
# CONFIGURAÇÃO
# ---------------------------------------------------
st.set_page_config(
    page_title="Alosa IA",
    page_icon="💬",
    layout="wide"
)

# ---------------------------------------------------
# CSS WHATSAPP STYLE
# ---------------------------------------------------
st.markdown("""
<style>
header, footer, #MainMenu {visibility: hidden;}

.stApp {
    background-color: #ECE5DD;
}

/* TEXTO PRETO GLOBAL */
html, body, p, div, span, label,
h1, h2, h3, h4, h5, h6 {
    color: #000000 !important;
}

/* CHAT */
.chat-container {
    display: flex;
    flex-direction: column;
    gap: 8px;
    padding-bottom: 80px;
}

/* BOLHAS */
.bubble {
    padding: 10px 14px;
    border-radius: 8px;
    max-width: 65%;
    font-size: 15px;
    line-height: 1.5;
    box-shadow: 0 1px 0 rgba(0,0,0,.1);
}

.user {
    background-color: #DCF8C6;
    margin-left: auto;
}

.bot {
    background-color: #FFFFFF;
    margin-right: auto;
}

.time {
    font-size: 10px;
    text-align: right;
    margin-top: 3px;
}

/* INPUT */
[data-testid="stChatInput"] textarea {
    background-color: #2b2b2b !important;
    color: #FFFFFF !important;
    border-radius: 20px;
}

textarea::placeholder {
    color: #BBBBBB !important;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# HORA BRASIL
# ---------------------------------------------------
def hora_brasil():
    brasil = timezone(timedelta(hours=-3))
    return datetime.now(brasil).strftime("%H:%M")

# ---------------------------------------------------
# CONTEXTO
# ---------------------------------------------------
def carregar_contexto():
    try:
        with open("instrucoes.txt", "r", encoding="utf-8") as f:
            return f.read()
    except:
        return "Você é o Alosa, assistente comercial."

# ---------------------------------------------------
# SESSION
# ---------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": carregar_contexto()}
    ]

# ---------------------------------------------------
# IA
# ---------------------------------------------------
def perguntar_ia(historico):
    token = st.secrets.get("HF_TOKEN")
    if not token:
        return "Token não configurado."

    API_URL = "https://router.huggingface.co/v1/chat/completions"

    payload = {
        "model": "meta-llama/Llama-3.2-3B-Instruct",
        "messages": historico,
        "max_tokens": 800,
        "temperature": 0.7
    }

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    r = requests.post(API_URL, headers=headers, json=payload)

    if r.status_code == 200:
        return r.json()["choices"][0]["message"]["content"]
    return "Erro ao gerar resposta."

# ---------------------------------------------------
# HEADER
# ---------------------------------------------------
st.title("💬 Alosa — Assistente IA")

# ---------------------------------------------------
# CHAT
# ---------------------------------------------------
st.markdown('<div class="chat-container">', unsafe_allow_html=True)

for msg in st.session_state.messages:
    if msg["role"] == "system":
        continue

    classe = "bot"
    if msg["role"] == "user":
        classe = "user"

    st.markdown(
        f"""
        <div class="bubble {classe}">
            {msg["content"]}
            <div class="time">{hora_brasil()}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------
# GERAR RESPOSTA DA IA
# ---------------------------------------------------
if st.session_state.messages[-1]["role"] == "user":
    with st.spinner("Digitando..."):
        resposta = perguntar_ia(st.session_state.messages)

    placeholder = st.empty()
    texto = ""

    for palavra in resposta.split(" "):
        texto += palavra + " "
        time.sleep(0.01)
        placeholder.markdown(
            f"""
            <div class="bubble bot">
                {texto}▌
                <div class="time">{hora_brasil()}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    placeholder.markdown(
        f"""
        <div class="bubble bot">
            {texto}
            <div class="time">{hora_brasil()}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.session_state.messages.append({
        "role": "assistant",
        "content": texto
    })

# ---------------------------------------------------
# INPUT
# ---------------------------------------------------
if prompt := st.chat_input("Digite uma mensagem"):
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })
    st.rerun()

# ---------------------------------------------------
# SIDEBAR
# ---------------------------------------------------
with st.sidebar:
    st.subheader("Controle")

    if st.button("Nova conversa"):
        st.session_state.messages = [
            {"role": "system", "content": carregar_contexto()}
        ]
        st.rerun()
