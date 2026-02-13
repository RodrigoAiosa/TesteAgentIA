import streamlit as st
import requests
import os
import pandas as pd
import time
from datetime import datetime
import io

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Chat IA Pro", page_icon="💬", layout="wide")

# --- INJEÇÃO DE CSS AVANÇADO ---
def apply_custom_style():
    img_url = "https://raw.githubusercontent.com/rodrigoaiosa/TesteAgentIA/main/AIOSA_LOGO.jpg"
    
    st.markdown(
        f"""
        <style>
        /* 1. OCULTAÇÃO DE INTERFACE (Botão Manage App e Menus) */
        header, footer, #MainMenu {{visibility: hidden !important;}}
        [data-testid="stAppDeployButton"], [data-testid="manage-app-button"], .stDeployButton {{
            display: none !important;
        }}

        /* 2. BACKGROUND E TELA */
        .stApp {{
            background-image: url("{img_url}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}

        /* 3. POSICIONAMENTO DO CLIPE DE ANEXO */
        /* Estilizamos o uploader para parecer um pequeno ícone de clipe flutuante */
        .stFileUploader {{
            position: fixed;
            bottom: 35px;
            left: 55px;
            width: 50px;
            z-index: 9999;
        }}
        .stFileUploader section {{
            padding: 0 !important;
            border: none !important;
            background: transparent !important;
        }}
        .stFileUploader label {{ display: none !important; }}
        
        /* Botão do Clipe */
        .stFileUploader button {{
            background-color: rgba(255, 255, 255, 0.2) !important;
            border: 1px solid rgba(255,255,255,0.4) !important;
            border-radius: 50% !important;
            height: 40px !important;
            width: 40px !important;
            color: white !important;
            box-shadow: 0px 4px 10px rgba(0,0,0,0.3);
        }}

        /* Ajuste do campo de input para não bater no clipe */
        [data-testid="stChatInput"] {{
            padding-left: 60px !important;
        }}

        /* 4. MENSAGENS DO CHAT */
        .stChatMessage {{
            background-color: rgba(255, 248, 231, 0.85) !important; 
            border-radius: 15px;
            border: 1px solid #8B4513;
            color: #000 !important;
        }}
        [data-testid="stChatMessageUser"] {{
            background-color: rgba(210, 180, 140, 0.95) !important;
            margin-left: auto !important;
            flex-direction: row-reverse !important;
        }}
        .stChatMessage p {{ color: black !important; font-weight: 500; }}

        /* 5. SIDEBAR */
        [data-testid="stSidebar"] {{ background-color: rgba(45, 28, 25, 0.98) !important; }}
        [data-testid="stSidebar"] * {{ color: #D2B48C !important; }}
        </style>
        """,
        unsafe_allow_html=True
    )

apply_custom_style()

# --- INICIALIZAÇÃO DE DADOS (Preservando Histórico) ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "tabela_dados" not in st.session_state:
    st.session_state.tabela_dados = pd.DataFrame(columns=["Data/Hora", "Pergunta", "Resposta"])

# --- ÁREA DE ANEXO (O Ícone de Clipe) ---
# O emoji 📎 funciona como o selo do botão de upload
arquivo_subido = st.file_uploader("📎", type=["csv", "xlsx"], key="upload_clipe")

contexto_excel = ""
if arquivo_subido:
    try:
        if arquivo_subido.name.endswith('.csv'):
            df = pd.read_csv(arquivo_subido)
        else:
            df = pd.read_excel(arquivo_subido)
        
        st.info(f"📁 Arquivo '{arquivo_subido.name}' carregado. (Ex: {df.shape[0]} linhas)")
        # Criamos um resumo para a IA entender a base
        contexto_excel = f"\n[Contexto da Planilha: {arquivo_subido.name}]\nColunas: {list(df.columns)}\nDados:\n{df.head(3).to_string()}"
    except Exception as e:
        st.error(f"Erro ao ler arquivo: {e}")

# --- TÍTULO E CHAT ---
st.title("💬 Sou o AIosa, seu assistente virtual...")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- LÓGICA DE ENVIO ---
if prompt := st.chat_input("Como posso ajudar?"):
    
    # Combinar pergunta com os dados da planilha se houver anexo
    prompt_com_dados = f"{prompt} {contexto_excel}" if contexto_excel else prompt
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""
        
        with st.spinner("Analisando manuscritos e dados..."):
            # Configuração da API
            HF_TOKEN = os.getenv("HF_TOKEN")
            API_URL = "https://router.huggingface.co/v1/chat/completions"
            headers = {"Authorization": f"Bearer {HF_TOKEN}", "Content-Type": "application/json"}
            
            payload = {
                "model": "meta-llama/Llama-3.2-3B-Instruct",
                "messages": st.session_state.messages[:-1] + [{"role": "user", "content": prompt_com_dados}],
                "max_tokens": 1000,
                "temperature": 0.5
            }
            
            try:
                response = requests.post(API_URL, headers=headers, json=payload)
                resposta_ia = response.json()["choices"][0]["message"]["content"]
            except:
                resposta_ia = "⚠️ Erro ao processar. Verifique sua conexão ou o arquivo."

        # Efeito de digitação
        for chunk in resposta_ia.split(" "):
            full_response += chunk + " "
            time.sleep(0.03)
            placeholder.markdown(full_response + "▌")
        placeholder.markdown(full_response)

    # Salvamento obrigatório na tabela e preservação do estado
    st.session_state.messages.append({"role": "assistant", "content": full_response})
    nova_linha = pd.DataFrame([{"Data/Hora": datetime.now().strftime("%H:%M:%S"), "Pergunta": prompt, "Resposta": full_response}])
    st.session_state.tabela_dados = pd.concat([st.session_state.tabela_dados, nova_linha], ignore_index=True)

# --- MENU LATERAL ---
with st.sidebar:
    st.subheader("Configurações")
    if st.button("Limpar Chat"):
        st.session_state.messages = []
        st.rerun()
    st.divider()
    st.caption(f"Interações salvas: {len(st.session_state.tabela_dados)}")
