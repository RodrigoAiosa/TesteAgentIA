import streamlit as st
import requests
import os
import pandas as pd
import time
from datetime import datetime
import io

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Chat IA Pro", page_icon="💬", layout="wide")

# --- INJEÇÃO DE CSS (Background, Ocultação e Clipe à Direita) ---
def apply_custom_style():
    img_url = "https://raw.githubusercontent.com/rodrigoaiosa/TesteAgentIA/main/AIOSA_LOGO.jpg"
    
    st.markdown(
        f"""
        <style>
        /* 1. OCULTAÇÃO DO BOTÃO MANAGE APP E BARRAS DE SISTEMA */
        header, footer, #MainMenu {{visibility: hidden !important;}}
        
        [data-testid="manage-app-button"], 
        ._terminalButton_rix23_138,
        [data-testid="stAppDeployButton"],
        .stDeployButton {{
            display: none !important;
            visibility: hidden !important;
        }}

        /* 2. BACKGROUND */
        .stApp {{
            background-image: url("{img_url}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}

        /* 3. POSICIONAMENTO DO CLIPE DE ANEXO (DIREITA) */
        /* Movemos o uploader para o lado direito, antes do botão de enviar */
        .stFileUploader {{
            position: fixed;
            bottom: 35px;
            right: 80px; /* Ajustado para ficar antes do ícone de enviar */
            width: 45px;
            z-index: 1000;
        }}
        
        .stFileUploader section {{
            padding: 0 !important;
            border: none !important;
            background: transparent !important;
        }}
        
        .stFileUploader label {{ display: none !important; }}

        .stFileUploader button {{
            background-color: rgba(255, 255, 255, 0.2) !important;
            border: 1px solid rgba(255,255,255,0.3) !important;
            border-radius: 50% !important;
            width: 38px !important;
            height: 38px !important;
            color: white !important;
        }}
        
        /* Ajuste do padding do input para acomodar o botão à direita */
        [data-testid="stChatInput"] {{
            padding-right: 65px !important;
        }}

        /* 4. ESTILO DAS MENSAGENS */
        .stChatMessage {{
            background-color: rgba(255, 248, 231, 0.8) !important; 
            border-radius: 15px;
            border: 1px solid #8B4513;
            color: #000 !important;
        }}
        [data-testid="stChatMessageUser"] {{
            background-color: rgba(210, 180, 140, 0.9) !important;
            margin-left: auto !important;
            flex-direction: row-reverse !important;
        }}
        .stChatMessage p {{ color: black !important; font-weight: 500; }}

        /* 5. SIDEBAR */
        [data-testid="stSidebar"] {{
            background-color: rgba(45, 28, 25, 0.98) !important; 
        }}
        [data-testid="stSidebar"] * {{ color: #D2B48C !important; }}
        </style>
        """,
        unsafe_allow_html=True
    )

apply_custom_style()

# --- INICIALIZAÇÃO E PRESERVAÇÃO DE DADOS ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "tabela_dados" not in st.session_state:
    st.session_state.tabela_dados = pd.DataFrame(columns=["Data/Hora", "Pergunta", "Resposta"])

# --- ÁREA DE TÍTULO ---
st.title("💬 Sou o AIosa, seu assistente virtual...")

# --- COMPONENTE DE ANEXO (Clipe à Direita) ---
arquivo_subido = st.file_uploader("📎", type=["csv", "xlsx"], key="clipe_right")

contexto_base = ""
if arquivo_subido:
    try:
        if arquivo_subido.name.endswith('.csv'):
            df = pd.read_csv(arquivo_subido)
        else:
            df = pd.read_excel(arquivo_subido)
        
        st.success(f"📌 Base '{arquivo_subido.name}' pronta.")
        # Amostra para a IA entender a estrutura
        contexto_base = f"\n[Dados do Arquivo]\nColunas: {df.columns.tolist()}\nVisualização:\n{df.head(3).to_string()}"
    except Exception as e:
        st.error(f"Erro ao processar: {e}")

# --- EXIBIÇÃO DO CHAT ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- LOGICA DE INPUT ---
if prompt := st.chat_input("O que deseja analisar na base?"):
    
    # Adiciona contexto do anexo se houver
    prompt_ia = f"{prompt} {contexto_base}" if contexto_base else prompt
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""
        
        with st.spinner("Analisando base de dados..."):
            HF_TOKEN = os.getenv("HF_TOKEN")
            API_URL = "https://router.huggingface.co/v1/chat/completions"
            headers = {"Authorization": f"Bearer {HF_TOKEN}", "Content-Type": "application/json"}
            payload = {
                "model": "meta-llama/Llama-3.2-3B-Instruct",
                "messages": st.session_state.messages[:-1] + [{"role": "user", "content": prompt_ia}],
                "max_tokens": 1000,
                "temperature": 0.5
            }
            
            try:
                response = requests.post(API_URL, headers=headers, json=payload)
                res_text = response.json()["choices"][0]["message"]["content"]
            except:
                res_text = "Desculpe, tive um problema ao processar sua análise."

        for chunk in res_text.split(" "):
            full_response += chunk + " "
            time.sleep(0.03)
            placeholder.markdown(full_response + "▌")
        placeholder.markdown(full_response)

    # Salvamento e preservação de dados
    st.session_state.messages.append({"role": "assistant", "content": full_response})
    nova_interacao = pd.DataFrame([{
        "Data/Hora": datetime.now().strftime("%H:%M:%S"), 
        "Pergunta": prompt, 
        "Resposta": full_response
    }])
    st.session_state.tabela_dados = pd.concat([st.session_state.tabela_dados, nova_interacao], ignore_index=True)

# --- MENU LATERAL ---
with st.sidebar:
    st.subheader("Configurações")
    if st.button("Limpar Chat"):
        st.session_state.messages = []
        st.rerun()
    st.divider()
    st.caption(f"Interações salvas: {len(st.session_state.tabela_dados)}")
