import streamlit as st
import requests
import os
import pandas as pd
import time
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Chat IA Pro", page_icon="💬", layout="wide")

# --- INJEÇÃO DE CSS PARA O BACKGROUND E ESTILO ---
def apply_custom_style():
    # Substitua pelo seu link direto (clique em 'Raw' no GitHub para obter o link correto)
    img_url = "https://raw.githubusercontent.com/seu-usuario/seu-repositorio/main/AIOSA_LOGO.jpg"
    
    st.markdown(
        f"""
        <style>
        /* Fundo principal do app */
        .stApp {{
            background-image: url("{img_url}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}

        /* Container do Chat para melhorar leitura sobre o fundo */
        .stChatMessage {{
            background-color: rgba(255, 248, 231, 0.85) !important; /* Bege pergaminho com transparência */
            border-radius: 15px;
            border: 1px solid #8B4513;
            margin-bottom: 10px;
            color: #3E2723 !important;
        }}

        /* Estilização específica da Sidebar */
        [data-testid="stSidebar"] {{
            background-color: rgba(62, 39, 35, 0.9) !important; /* Marrom escuro da imagem */
        }}
        [data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] p {{
            color: #D2B48C !important; /* Texto em tom areia */
        }}

        /* Título Principal */
        h1 {{
            color: #3E2723 !important;
            text-shadow: 2px 2px 4px rgba(255,255,255,0.7);
            font-family: 'serif';
        }}

        /* Ajuste do campo de input */
        .stChatInputContainer {{
            background-color: rgba(255, 255, 255, 0.1) !important;
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

# --- INICIALIZAÇÃO DE ESTADOS ---
if "messages" not in st.session_state:
    st.session_state.messages = []

if "tabela_dados" not in st.session_state:
    # Preservando dados conforme instrução: salvando novos e mantendo existentes
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
        
        with st.spinner("Consultando arquivos..."):
            resposta_bruta = perguntar_ia(st.session_state.messages)
        
        for chunk in resposta_bruta.split(" "):
            full_response += chunk + " "
            time.sleep(0.04)
            placeholder.markdown(full_response + "▌")
        placeholder.markdown(full_response)

    # Salvamento de dados (sempre preservando o histórico anterior)
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
    # Indicador discreto do histórico salvo
    st.caption(f"Interações documentadas: {len(st.session_state.tabela_dados)}")
