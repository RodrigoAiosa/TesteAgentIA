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
# CSS WHATSAPP STYLE (REMOÇÃO AGRESSIVA DE RODAPÉ E FAIXA DE INPUT)
# ---------------------------------------------------
st.markdown("""
<style>
/* 1. ESCONDER ELEMENTOS NATIVOS */
header {visibility: hidden;}
footer {visibility: hidden;}
#MainMenu {visibility: hidden;}
[data-testid="stStatusWidget"] {visibility: hidden;}
.stAppDeployButton {display: none !important;}

/* 2. REMOVER O FUNDO ESCURO DA ÁREA DE INPUT (O "RODAPÉ" QUE VOCÊ VIU) */
[data-testid="stChatInput"] {
    background-color: transparent !important;
    padding-bottom: 20px !important;
}

/* 3. AJUSTAR O FUNDO GERAL */
.stApp {
    background-color: #ECE5DD;
}

/* 4. ESTILIZAR A CAIXA DE TEXTO PARA NÃO PARECER UM BLOCO PRETO */
[data-testid="stChatInput"] textarea {
    background-color: #FFFFFF !important;
    color: #000000 !important;
    border-radius: 20px !important;
    border: 1px solid #CCCCCC !important;
}

/* 5. TEXTO PRETO NAS BOLHAS E GERAL */
html, body, p, div, span, label, h1, h2, h3, h4, h5, h6 {
    color: #000000 !important;
}

.chat-container {
    display: flex;
    flex-direction: column;
    padding-bottom: 50px;
}

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

/* REMOVER ESPAÇAMENTOS EXTRAS NO TOPO */
.block-container {
    padding-top: 1rem !important;
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
# INICIALIZAÇÃO E LÓGICA
# ---------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": carregar_contexto()}]

def perguntar_ia(historico):
    token = st.secrets.get("HF_TOKEN")
    if not token: return "Erro: Token HF_TOKEN não configurado."
    
    ultima_msg = historico[-1]["content"].lower()
    gatilhos = ["preço", "valor", "mentoria", "quanto custa", "orçamento", "treinamento", "custo"]
    
    API_URL = "https://router.huggingface.co/v1/chat/completions"
    payload = {
        "model": "meta-llama/Llama-3.2-3B-Instruct",
        "messages": historico,
        "max_tokens": 800,
        "temperature": 0.7
    }
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    try:
        r = requests.post(API_URL, headers=headers, json=payload)
        if r.status_code == 200:
            resposta = r.json()["choices"][0]["message"]["content"]
            if any(g in ultima_msg for g in gatilhos) and "11977019335" not in resposta:
                resposta += f"\n\nPara um orçamento personalizado, fale com o Rodrigo:\n"
                resposta += f"📱 WhatsApp: 11 97701-9335\n📧 E-mail: rodrigoaiosa@gmail.com"
            return resposta
    except:
        return "Erro ao processar resposta."
    return "Erro ao gerar resposta."

st.title("💬 Alosa — Assistente IA")
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

renderizar_mensagens()

if prompt := st.chat_input("Digite uma mensagem"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    salvar_no_historico("Usuário", prompt)
    st.rerun()

if st.session_state.messages[-1]["role"] == "user":
    with st.spinner("Digitando..."):
        resposta_final = perguntar_ia(st.session_state.messages)
        st.session_state.messages.append({"role": "assistant", "content": resposta_final})
        salvar_no_historico("Alosa IA", resposta_final)
    st.rerun()

with st.sidebar:
    if st.button("Nova Conversa"):
        st.session_state.messages = [{"role": "system", "content": carregar_contexto()}]
        st.rerun()
