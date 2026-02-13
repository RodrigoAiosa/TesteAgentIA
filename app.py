import streamlit as st
import requests
import os
import pandas as pd
import time
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Chat IA Pro", page_icon="✍️", layout="wide")

# --- INJEÇÃO DE CSS (FOCO EM TEXTO PRETO E LEGIBILIDADE MÁXIMA) ---
def apply_custom_style():
    img_url = "https://raw.githubusercontent.com/rodrigoaiosa/TesteAgentIA/main/AIOSA_LOGO.jpg"
    
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=EB+Garamond:wght@500;700&display=swap');

        /* 1. OCULTAÇÃO DE INTERFACE DE SISTEMA */
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

        /* 3. TEXTOS EM PRETO (FORÇADO PARA LEGIBILIDADE) */
        h1 {{
            color: #000000 !important;
            font-family: 'EB Garamond', serif;
            font-weight: 700;
            text-shadow: none !important;
        }}

        /* Mensagens do Chat */
        .stChatMessage {{
            background-color: rgba(255, 248, 231, 0.95) !important; 
            border: 1px solid #8B4513;
            border-radius: 15px;
        }}

        /* Força a cor PRETA em todos os textos de mensagens */
        .stChatMessage .stMarkdown p, 
        .stChatMessage [data-testid="stMarkdownContainer"] p,
        .stChatMessage span,
        .stChatMessage code {{
            color: #000000 !important;
            font-family: 'EB Garamond', serif;
            font-size: 1.3rem !important;
            font-weight: 500 !important;
        }}

        /* Balão do Usuário */
        [data-testid="stChatMessageUser"] {{
            background-color: rgba(210, 180, 140, 1.0) !important;
        }}

        /* 4. CAMPO DE ENTRADA (INPUT) */
        .stChatInputContainer textarea {{
            color: #000000 !important;
            -webkit-text-fill-color: #000000 !important;
            font-weight: 600 !important;
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

# --- INICIALIZAÇÃO E MEMÓRIA ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "tabela_dados" not in st.session_state:
    st.session_state.tabela_dados = pd.DataFrame(columns=["Data/Hora", "Pergunta", "Resposta"])

# --- FUNÇÃO DA IA (COM TRATAMENTO DE ERRO DETALHADO) ---
def perguntar_ia(historico):
    # Janela de memória: enviamos apenas as últimas 8 mensagens
    contexto = historico[-8:] if len(historico) > 8 else historico
    
    HF_TOKEN = os.getenv("HF_TOKEN")
    API_URL = "https://router.huggingface.co/v1/chat/completions"
    headers = {"Authorization": f"Bearer {HF_TOKEN}", "Content-Type": "application/json"}
    
    payload = {
        "model": "meta-llama/Llama-3.2-3B-Instruct",
        "messages": contexto,
        "max_tokens": 800,
        "temperature": 0.5
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=15)
        
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        elif response.status_code == 401:
            return "⚠️ Erro de Autenticação: Verifique se o seu HF_TOKEN está correto nas Secrets."
        elif response.status_code == 429:
            return "⚠️ Limite Excedido: Muitas requisições ao modelo. Tente novamente em alguns instantes."
        else:
            return f"⚠️ Erro na API (Status {response.status_code}): {response.text}"
            
    except requests.exceptions.Timeout:
        return "⚠️ O tempo de resposta esgotou. A conexão com o servidor está lenta."
    except Exception as e:
        return f"⚠️ Erro inesperado: {str(e)}"

# --- INTERFACE ---
st.title("💬 Sou o Alosa, seu assistente virtual...")

# Exibe histórico
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- PROCESSAMENTO ---
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
        
        # Só faz o efeito de digitação se não for uma mensagem de erro curta
        if resposta.startswith("⚠️"):
            placeholder.error(resposta)
            full_res = resposta
        else:
            for chunk in resposta.split(" "):
                full_res += chunk + " "
                time.sleep(0.02)
                placeholder.markdown(full_res + "▌")
            placeholder.markdown(full_res)

    # Salvamento de Dados (Preservando o histórico conforme instruído)
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
    st.write(f"Interações: {len(st.session_state.tabela_dados)}")
