import streamlit as st
import requests
import os
import pandas as pd
import time
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Chat IA Pro", page_icon="💬", layout="wide")

# --- INJEÇÃO DE CSS PARA O BACKGROUND PROPORCIONAL E ESTILOS ---
def apply_custom_style():
    # Link direto da sua imagem no GitHub
    img_url = "https://raw.githubusercontent.com/rodrigoaiosa/TesteAgentIA/main/AIOSA_LOGO.jpg"
    
    st.markdown(
        f"""
        <style>
        /* Ajuste do Background para ficar proporcional */
        .stApp {{
            background-image: url("{img_url}");
            background-size: cover; /* Mantém a proporção sem deformar */
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}

        /* Título Principal em BRANCO */
        h1 {{
            color: #FFFFFF !important;
            text-shadow: 2px 2px 10px rgba(0,0,0,0.9);
            font-family: 'serif';
            font-weight: bold;
        }}

        /* Todos os textos do chat em PRETO */
        [data-testid="stChatMessage"] .stMarkdown p, 
        [data-testid="stChatMessage"] .stMarkdown li {{
            color: #000000 !important;
            font-weight: 500;
        }}

        /* Balões de Chat com fundo pergaminho suave */
        .stChatMessage {{
            background-color: rgba(255, 248, 231, 0.8) !important; 
            border-radius: 15px;
            border: 1px solid #8B4513;
            margin-bottom: 10px;
            box-shadow: 2px 2px 5px rgba(0,0,0,0.2);
        }}

        /* Sidebar - Fundo Marrom e Texto Areia */
        [data-testid="stSidebar"] {{
            background-color: rgba(45, 28, 25, 0.98) !important; 
        }}
        [data-testid="stSidebar"] .stMarkdown p, 
        [data-testid="stSidebar"] h3, 
        [data-testid="stSidebar"] span {{
            color: #D2B48C !important;
        }}

        /* Estilização do Campo de Entrada (Input) */
        .stChatInputContainer {{
            background-color: rgba(255, 255, 255, 0.15) !important;
            border-radius: 10px;
        }}
        
        /* Corrigindo ícones e labels auxiliares para preto no chat */
        .stChatMessage [data-testid="stMarkdownContainer"] {{
            color: #000000 !important;
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

headers = {
    "Authorization": f"Bearer {HF_TOKEN}",
    "Content-Type": "application/json",
}

# --- INICIALIZAÇÃO DE ESTADOS (Preservando dados conforme solicitado) ---
if "messages" not in st.session_state:
    st.session_state.messages = []

if "tabela_dados" not in st.session_state:
    # Salvando novos dados e preservando existentes
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
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            return f"⚠️ Erro: {response.status_code}"
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
        
        with st.spinner("Consultando manuscritos..."):
            resposta_bruta = perguntar_ia(st.session_state.messages)
        
        # Efeito de digitação
        for chunk in resposta_bruta.split(" "):
            full_response += chunk + " "
            time.sleep(0.04)
            placeholder.markdown(full_response + "▌")
        placeholder.markdown(full_response)

    # Salvamento de dados e preservação de histórico conforme instrução
    st.session_state.messages.append({"role": "assistant", "content": full_response})
    
    nova_linha = pd.DataFrame([{
        "Data/Hora": datetime.now().strftime("%H:%M:%S"),
        "Pergunta": prompt,
        "Resposta": full_response
    }])
    st.session_state.tabela_dados = pd.concat([st.session_state.tabela_dados, nova_linha], ignore_index=True)

# --- MENU LATERAL ---
with st.sidebar:
    st.subheader("Configurações")
    if st.button("Limpar Chat"):
        st.session_state.messages = []
        st.rerun()
    
    st.divider()
    # Mantendo registro das interações conforme solicitado
    st.caption(f"Interações documentadas nesta sessão: {len(st.session_state.tabela_dados)}")
