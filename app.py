import streamlit as st
import requests
import os
import pandas as pd
import time
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Alosa IA - Rodrigo Aiosa", page_icon="✍️", layout="wide")

# --- INJEÇÃO DE CSS (ESTILO EXECUTIVO PRETO ABSOLUTO) ---
def apply_custom_style():
    img_url = "https://raw.githubusercontent.com/rodrigoaiosa/TesteAgentIA/main/AIOSA_LOGO.jpg"
    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=EB+Garamond:wght@600;800&display=swap');
        
        header, footer, #MainMenu {{visibility: hidden !important;}}
        [data-testid="stAppDeployButton"] {{ display: none !important; }}

        .stApp {{
            background-image: url("{img_url}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}

        /* FORÇAR PRETO EM TODOS OS TEXTOS E LISTAS */
        h1, h2, h3, p, span, li, div, label, .stMarkdown, [data-testid="stChatMessageContent"] {{
            color: #000000 !important;
            font-family: 'EB Garamond', serif !important;
        }}

        .stChatMessage .stMarkdown p, 
        .stChatMessage .stMarkdown li,
        .stChatMessage span {{
            color: #000000 !important;
            font-size: 1.30rem !important;
            font-weight: 700 !important;
        }}

        /* Links em azul forte para destaque no fundo claro */
        .stChatMessage a {{
            color: #0000FF !important;
            text-decoration: underline !important;
            font-weight: 800 !important;
        }}

        .stChatMessage {{
            background-color: rgba(255, 255, 255, 0.96) !important;
            border: 2px solid #5D4037;
            border-radius: 12px;
            margin-bottom: 15px;
        }}

        [data-testid="stChatMessageUser"] {{ background-color: #E0C9A6 !important; }}

        .stChatInputContainer textarea {{ 
            color: #000000 !important; 
            font-weight: 600 !important; 
        }}
        </style>
    """, unsafe_allow_html=True)

apply_custom_style()

# --- CARREGAR CONHECIMENTO ---
def carregar_contexto():
    try:
        with open("instrucoes.txt", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "Você é o Alosa, assistente comercial do Rodrigo Aiosa."

# --- INICIALIZAÇÃO DA SESSÃO ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": carregar_contexto()}]

if "tabela_dados" not in st.session_state:
    st.session_state.tabela_dados = pd.DataFrame(columns=["Data/Hora", "Pergunta", "Resposta"])

# --- INTEGRAÇÃO COM IA ---
def perguntar_ia(historico):
    token = st.secrets.get("HF_TOKEN")
    if not token: return "⚠️ Token HF_TOKEN não configurado nas Secrets."
    API_URL = "https://router.huggingface.co/v1/chat/completions"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    payload = {"model": "meta-llama/Llama-3.2-3B-Instruct", "messages": historico, "max_tokens": 1000, "temperature": 0.7}
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
        return response.json()["choices"][0]["message"]["content"] if response.status_code == 200 else "⚠️ Erro de API."
    except Exception: return "⚠️ Erro de conexão com o servidor."

# --- INTERFACE DE CHAT ---
st.title("💬 Sou o Alosa, como posso escalar seu negócio?")

for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"], avatar="👤" if msg["role"] == "user" else "✍️"):
            st.markdown(msg["content"])

if prompt := st.chat_input("Descreva seu desafio ou interesse..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"): st.markdown(prompt)

    with st.chat_message("assistant", avatar="✍️"):
        placeholder = st.empty()
        with st.spinner("Analisando sua demanda estratégica..."):
            resposta = perguntar_ia(st.session_state.messages)
        
        full_res = ""
        for chunk in resposta.split(" "):
            full_res += chunk + " "
            time.sleep(0.01)
            placeholder.markdown(full_res + "▌")
        placeholder.markdown(full_res)

    st.session_state.messages.append({"role": "assistant", "content": full_res})
    
    # PRESERVAR DADOS NA TABELA INTERNA
    nova_linha = pd.DataFrame([{"Data/Hora": datetime.now().strftime("%H:%M:%S"), "Pergunta": prompt, "Resposta": full_res}])
    st.session_state.tabela_dados = pd.concat([st.session_state.tabela_dados, nova_linha], ignore_index=True)

# --- BARRA LATERAL ---
with st.sidebar:
    st.subheader("📜 Painel de Gestão")
    if st.button("Nova Conversa"):
        st.session_state.messages = [{"role": "system", "content": carregar_contexto()}]
        st.rerun()
    st.write(f"Leads qualificados: {len(st.session_state.tabela_dados)}")
    st.markdown("---")
    wa_link = "https://wa.me/5511977019335?text=Oi,%20Rodrigo!%20Vim%20pelo%20Chat%20IA."
    st.markdown(f"**WhatsApp Direto:** [(11) 97701-9335]({wa_link})")
    st.markdown(f"**E-mail:** [contato@aiosa.com.br](mailto:contato@aiosa.com.br)")
