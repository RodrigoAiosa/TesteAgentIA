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

/* CHAT CONTAINER */
.chat-container {
    display: flex;
    flex-direction: column;
    padding-bottom: 100px;
}

/* BOLHAS COM ESPAÇAMENTO */
.bubble {
    padding: 10px 14px;
    border-radius: 8px;
    max-width: 75%;
    font-size: 15px;
    line-height: 1.5;
    box-shadow: 0 1px 0 rgba(0,0,0,.1);
    margin-bottom: 15px; /* DISTÂNCIA ENTRE AS MENSAGENS */
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

/* INPUT PERSONALIZADO (#262730) */
[data-testid="stChatInput"] {
    padding-bottom: 20px;
}

[data-testid="stChatInput"] textarea {
    background-color: #262730 !important; /* COR SOLICITADA */
    color: #FFFFFF !important; /* TEXTO BRANCO PARA CONTRASTE */
    border-radius: 20px;
    border: 1px solid #3e404b !important;
}

textarea::placeholder {
    color: #BBBBBB !important;
}

/* BOTÃO DE ENVIO */
[data-testid="stChatInput"] button {
    background-color: transparent !important;
    color: #FFFFFF !important;
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
    contatos = "\n\nIMPORTANTE: Se o usuário perguntar sobre preços, valores, treinamentos ou mentorias, explique que o orçamento é personalizado e forneça OBRIGATORIAMENTE os contatos: WhatsApp: 11977019335 e E-mail: rodrigoaiosa@gmail.com."
    try:
        with open("instrucoes.txt", "r", encoding="utf-8") as f:
            return f.read() + contatos
    except:
        return "Você é o Alosa, assistente comercial." + contatos

# ---------------------------------------------------
# SESSION
# ---------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": carregar_contexto()}
    ]

# ---------------------------------------------------
# IA COM LÓGICA DE CONTATO
# ---------------------------------------------------
def perguntar_ia(historico):
    token = st.secrets.get("HF_TOKEN")
    if not token:
        return "Erro: Configure o HF_TOKEN nos Secrets."

    ultima_msg_user = historico[-1]["content"].lower()
    # Gatilhos para enviar contatos
    gatilhos = ["preço", "valor", "quanto custa", "orçamento", "treinamento", "mentoria", "custo", "pagamento"]
    
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

    try:
        r = requests.post(API_URL, headers=headers, json=payload)
        if r.status_code == 200:
            resposta = r.json()["choices"][0]["message"]["content"]
            
            # Verificação de segurança para garantir o envio dos contatos
            if any(g in ultima_msg_user for g in gatilhos) and "11977019335" not in resposta:
                resposta += "\n\nPara te passar um orçamento detalhado e personalizado sobre treinamentos ou mentoria, por favor entre em contato:\n"
                resposta += "📱 WhatsApp: 11 97701-9335\n"
                resposta += "📧 E-mail: rodrigoaiosa@gmail.com"
            
            return resposta
    except:
        return "Erro ao processar sua solicitação."
    
    return "Erro ao gerar resposta."

# ---------------------------------------------------
# HEADER
# ---------------------------------------------------
st.title("💬 Alosa — Assistente IA")

# ---------------------------------------------------
# EXIBIÇÃO DAS MENSAGENS
# ---------------------------------------------------
chat_placeholder = st.container()

with chat_placeholder:
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    for msg in st.session_state.messages:
        if msg["role"] == "system":
            continue

        classe = "user" if msg["role"] == "user" else "bot"
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
# INPUT E RESPOSTA
# ---------------------------------------------------
if prompt := st.chat_input(""):
    # Adiciona a pergunta à sessão
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Gera a resposta
    with st.spinner("Digitando..."):
        resposta_ia = perguntar_ia(st.session_state.messages)
        st.session_state.messages.append({"role": "assistant", "content": resposta_ia})
    
    st.rerun()

# ---------------------------------------------------
# SIDEBAR
# ---------------------------------------------------
with st.sidebar:
    st.subheader("Opções")
    if st.button("Limpar Histórico"):
        st.session_state.messages = [{"role": "system", "content": carregar_contexto()}]
        st.rerun()
