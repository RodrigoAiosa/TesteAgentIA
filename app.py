import streamlit as st
import requests
import time
import os
from datetime import datetime, timedelta, timezone

# ---------------------------------------------------
# CONFIGURAÇÃO DA PÁGINA
# ---------------------------------------------------
st.set_page_config(
    page_title="Alosa IA",
    page_icon="💬",
    layout="wide"
)

# ---------------------------------------------------
# CSS WHATSAPP STYLE (COM REMOÇÃO DE RODAPÉ)
# ---------------------------------------------------
st.markdown("""
<style>
/* ESCONDER HEADER, RODAPÉ E MENU PADRÃO */
header, footer, #MainMenu {visibility: hidden;}
[data-testid="stStatusWidget"] {visibility: hidden;}

.stApp {
    background-color: #ECE5DD;
}

/* TEXTO PRETO NAS BOLHAS */
html, body, p, div, span, label,
h1, h2, h3, h4, h5, h6 {
    color: #000000 !important;
}

.chat-container {
    display: flex;
    flex-direction: column;
    padding-bottom: 100px;
}

/* DISTÂNCIA ENTRE AS CAIXAS DE MENSAGENS */
.bubble {
    padding: 10px 14px;
    border-radius: 8px;
    max-width: 75%;
    font-size: 15px;
    line-height: 1.5;
    box-shadow: 0 1px 0 rgba(0,0,0,.1);
    margin-bottom: 15px; 
    position: relative;
}

.user {
    background-color: #DCF8C6;
    margin-left: auto;
    align-self: flex-end;
}

.bot {
    background-color: #FFFFFF;
    margin-right: auto;
    align-self: flex-start;
}

.time {
    font-size: 10px;
    text-align: right;
    margin-top: 5px;
    color: #666 !important;
}

/* CAIXA DE TEXTO DO USUÁRIO (#262730) */
[data-testid="stChatInput"] textarea {
    background-color: #262730 !important;
    color: #FFFFFF !important;
    border-radius: 20px;
    border: 1px solid #3e404b !important;
    padding-left: 20px !important; /* CURSOR COM RECUO */
}

textarea::placeholder {
    color: #BBBBBB !important;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# FUNÇÕES DE APOIO
# ---------------------------------------------------
def hora_brasil():
    brasil = timezone(timedelta(hours=-3))
    return datetime.now(brasil).strftime("%d/%m/%Y %H:%M:%S")

def salvar_no_historico(role, content):
    """Salva a mensagem no arquivo .txt preservando dados existentes."""
    data_hora = hora_brasil()
    linha = f"[{data_hora}] {role.upper()}: {content}\n"
    with open("historico.txt", "a", encoding="utf-8") as f:
        f.write(linha)

def carregar_contexto():
    try:
        with open("instrucoes.txt", "r", encoding="utf-8") as f:
            return f.read()
    except:
        return "Você é o Alosa, assistente comercial do Rodrigo Aiosa."

# ---------------------------------------------------
# INICIALIZAÇÃO DO ESTADO
# ---------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": carregar_contexto()}]

# ---------------------------------------------------
# LÓGICA DA IA
# ---------------------------------------------------
def perguntar_ia(historico):
    token = st.secrets.get("HF_TOKEN")

    if not token:
        return "Erro: Token HF_TOKEN não configurado."

    API_URL = "https://api-inference.huggingface.co/v1/chat/completions"

    payload = {
        "model": "meta-llama/Meta-Llama-3-8B-Instruct",
        "messages": historico,
        "max_tokens": 800,
        "temperature": 0.7
    }

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    try:
        r = requests.post(API_URL, headers=headers, json=payload)

        # 👇 DEBUG
        return f"STATUS: {r.status_code} | RESPOSTA: {r.text}"

    except Exception as e:
        return f"Erro interno: {str(e)}"

# ---------------------------------------------------
# RENDERIZAÇÃO E FLUXO DO CHAT
# ---------------------------------------------------
st.title("💬 Alosa — Assistente IA")

# Container fixo para mensagens
chat_container = st.container()

def renderizar_mensagens():
    with chat_container:
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        for msg in st.session_state.messages:
            if msg["role"] == "system": continue
            classe = "user" if msg["role"] == "user" else "bot"
            st.markdown(
                f'<div class="bubble {classe}">{msg["content"]}<div class="time">{hora_brasil().split(" ")[1]}</div></div>', 
                unsafe_allow_html=True
            )
        st.markdown('</div>', unsafe_allow_html=True)

# Renderiza as mensagens atuais
renderizar_mensagens()

# Input do usuário
if prompt := st.chat_input("Digite uma mensagem"):
    # 1. Adiciona à sessão e salva no arquivo imediatamente
    st.session_state.messages.append({"role": "user", "content": prompt})
    salvar_no_historico("Usuário", prompt)
    
    # 2. Rerun para mostrar a mensagem do usuário na tela ANTES da IA responder
    st.rerun()

# Se a última mensagem for do usuário, chama a IA
if st.session_state.messages[-1]["role"] == "user":
    with st.spinner("Digitando..."):
        resposta_final = perguntar_ia(st.session_state.messages)
        st.session_state.messages.append({"role": "assistant", "content": resposta_final})
        salvar_no_historico("Alosa IA", resposta_final)
    
    # 3. Rerun para mostrar a resposta da IA
    st.rerun()

# ---------------------------------------------------
# SIDEBAR
# ---------------------------------------------------
with st.sidebar:
    if st.button("Nova Conversa"):
        st.session_state.messages = [{"role": "system", "content": carregar_contexto()}]
        st.rerun()
