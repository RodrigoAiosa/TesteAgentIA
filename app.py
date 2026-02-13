import streamlit as st
import requests
import os
import pandas as pd
import time
from datetime import datetime
import io

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Chat IA Pro", page_icon="💬", layout="wide")

# --- INJEÇÃO DE CSS (Background, Ocultação e Posicionamento do Clipe) ---
def apply_custom_style():
    img_url = "https://raw.githubusercontent.com/rodrigoaiosa/TesteAgentIA/main/AIOSA_LOGO.jpg"
    
    st.markdown(
        f"""
        <style>
        /* 1. OCULTAÇÃO TOTAL DO SISTEMA */
        header, footer, #MainMenu {{visibility: hidden !important;}}
        [data-testid="manage-app-button"], 
        [data-testid="stAppDeployButton"],
        .stDeployButton,
        div[class*="terminalButton"] {{
            display: none !important;
            visibility: hidden !important;
        }}

        /* 2. BACKGROUND PROPORCIONAL */
        .stApp {{
            background-image: url("{img_url}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}

        /* 3. ESTILIZAÇÃO DO CHAT E TEXTOS */
        h1 {{ color: #FFFFFF !important; text-shadow: 2px 2px 10px rgba(0,0,0,0.9); }}
        
        .stChatMessage {{
            background-color: rgba(255, 248, 231, 0.8) !important; 
            border-radius: 15px;
            border: 1px solid #8B4513;
            margin-bottom: 15px;
            max-width: 80%;
        }}
        [data-testid="stChatMessageUser"] {{ margin-left: auto !important; flex-direction: row-reverse !important; background-color: rgba(210, 180, 140, 0.9) !important; }}
        .stChatMessage p {{ color: #000000 !important; font-weight: 500; }}

        /* 4. POSICIONAMENTO DO ÍCONE DE CLIPE (Anexo) */
        /* Movemos o uploader para sobrepor a barra de input */
        .stFileUploader {{
            position: fixed;
            bottom: 34px;
            left: 50px;
            width: 45px;
            z-index: 1000;
        }}
        
        /* Estiliza o botão de upload para parecer um ícone de clipe */
        .stFileUploader section {{
            padding: 0 !important;
            border: none !important;
            background: transparent !important;
        }}
        
        .stFileUploader label {{
            display: none !important;
        }}

        .stFileUploader button {{
            background-color: rgba(255, 255, 255, 0.2) !important;
            border: 1px solid rgba(255,255,255,0.3) !important;
            border-radius: 50% !important;
            width: 40px !important;
            height: 40px !important;
            color: white !important;
        }}
        
        /* Ajuste da margem do input para não sobrepor o clipe */
        [data-testid="stChatInput"] {{
            padding-left: 55px !important;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

apply_custom_style()

# --- ESTADOS E PRESERVAÇÃO DE DADOS ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "tabela_dados" not in st.session_state:
    st.session_state.tabela_dados = pd.DataFrame(columns=["Data/Hora", "Pergunta", "Resposta"])

# --- FUNÇÃO DE CONSULTA ---
def perguntar_ia(mensagens):
    HF_TOKEN = os.getenv("HF_TOKEN")
    API_URL = "https://router.huggingface.co/v1/chat/completions"
    headers = {"Authorization": f"Bearer {HF_TOKEN}", "Content-Type": "application/json"}
    payload = {
        "model": "meta-llama/Llama-3.2-3B-Instruct",
        "messages": mensagens,
        "max_tokens": 800,
        "temperature": 0.5
    }
    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        return response.json()["choices"][0]["message"]["content"]
    except:
        return "Erro ao processar análise."

# --- INTERFACE ---
st.title("💬 Sou o AIosa, seu assistente virtual...")

# Exibição do histórico
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- COMPONENTE DE ANEXO (Clipe) ---
# O ícone é renderizado através do botão de upload estilizado
arquivo_subido = st.file_uploader("📎", type=["csv", "xlsx"], key="clipe_upload")

contexto_arquivo = ""
if arquivo_subido:
    try:
        if arquivo_subido.name.endswith('.csv'):
            df = pd.read_csv(arquivo_subido)
        else:
            df = pd.read_excel(arquivo_subido)
        
        st.info(f"📊 Arquivo '{arquivo_subido.name}' pronto para análise.")
        # Extrai estrutura e amostra para a IA
        contexto_arquivo = f"\n[Arquivo Anexo: {arquivo_subido.name}]\nEstrutura: {df.columns.tolist()}\nExemplo:\n{df.head(3).to_string()}"
    except Exception as e:
        st.error(f"Erro no arquivo: {e}")

# --- BARRA DE CHAT ---
if prompt := st.chat_input("O que deseja analisar na base?"):
    
    # Adicionar o contexto do arquivo ao prompt se houver um anexo
    prompt_completo = f"{prompt} {contexto_arquivo}" if contexto_arquivo else prompt
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Analisando..."):
            resposta = perguntar_ia(st.session_state.messages + [{"role": "user", "content": prompt_completo}])
            placeholder = st.empty()
            full_res = ""
            for chunk in resposta.split(" "):
                full_res += chunk + " "
                time.sleep(0.02)
                placeholder.markdown(full_res + "▌")
            placeholder.markdown(full_res)

    # Salvamento e preservação
    st.session_state.messages.append({"role": "assistant", "content": full_res})
    nova_linha = pd.DataFrame([{"Data/Hora": datetime.now().strftime("%H:%M:%S"), "Pergunta": prompt, "Resposta": full_res}])
    st.session_state.tabela_dados = pd.concat([st.session_state.tabela_dados, nova_linha], ignore_index=True)

# --- SIDEBAR ---
with st.sidebar:
    st.subheader("Configurações")
    if st.button("Limpar Chat"):
        st.session_state.messages = []
        st.rerun()
    st.divider()
    st.caption(f"Interações salvas: {len(st.session_state.tabela_dados)}")
