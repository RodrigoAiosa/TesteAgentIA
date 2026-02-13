import streamlit as st
import requests
import os
import pandas as pd
import time
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
# Nota: Para arquivos de 100MB, se rodar localmente, use: streamlit run app.py --server.maxUploadSize 100
st.set_page_config(page_title="Chat IA Pro", page_icon="💬", layout="wide")

# --- INJEÇÃO DE CSS (Background, Ocultação e Estilo) ---
def apply_custom_style():
    img_url = "https://raw.githubusercontent.com/rodrigoaiosa/TesteAgentIA/main/AIOSA_LOGO.jpg"
    
    st.markdown(
        f"""
        <style>
        /* OCULTAÇÃO DO BOTÃO MANAGE APP E COMPONENTES DE SISTEMA */
        header, footer, #MainMenu {{visibility: hidden !important;}}
        [data-testid="manage-app-button"], 
        ._terminalButton_rix23_138,
        [data-testid="stAppDeployButton"],
        .stDeployButton {{
            display: none !important;
            visibility: hidden !important;
        }}

        /* BACKGROUND PROPORCIONAL */
        .stApp {{
            background-image: url("{img_url}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}

        /* TÍTULO EM BRANCO */
        h1 {{
            color: #FFFFFF !important;
            text-shadow: 2px 2px 10px rgba(0,0,0,0.9);
            font-family: 'serif';
        }}

        /* CHAT ALTERNADO */
        .stChatMessage {{
            background-color: rgba(255, 248, 231, 0.8) !important; 
            border-radius: 15px;
            border: 1px solid #8B4513;
            margin-bottom: 15px;
            max-width: 80%;
        }}
        [data-testid="stChatMessageUser"] {{
            margin-left: auto !important;
            flex-direction: row-reverse !important;
            background-color: rgba(210, 180, 140, 0.9) !important;
        }}
        [data-testid="stChatMessageAssistant"] {{
            margin-right: auto !important;
        }}
        .stChatMessage p {{
            color: #000000 !important;
            font-weight: 500;
        }}

        /* SIDEBAR */
        [data-testid="stSidebar"] {{
            background-color: rgba(45, 28, 25, 0.98) !important; 
        }}
        [data-testid="stSidebar"] .stMarkdown p, [data-testid="stSidebar"] h3 {{
            color: #D2B48C !important;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

apply_custom_style()

# --- INICIALIZAÇÃO DE ESTADOS ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "tabela_dados" not in st.session_state:
    st.session_state.tabela_dados = pd.DataFrame(columns=["Data/Hora", "Pergunta", "Resposta"])

# --- FUNÇÃO DE CONSULTA À IA ---
def perguntar_ia(mensagens):
    HF_TOKEN = os.getenv("HF_TOKEN")
    API_URL = "https://router.huggingface.co/v1/chat/completions"
    headers = {"Authorization": f"Bearer {HF_TOKEN}", "Content-Type": "application/json"}
    payload = {
        "model": "meta-llama/Llama-3.2-3B-Instruct",
        "messages": mensagens,
        "max_tokens": 1000,
        "temperature": 0.5
    }
    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        return response.json()["choices"][0]["message"]["content"]
    except:
        return "Desculpe, tive um problema ao processar sua análise."

# --- INTERFACE PRINCIPAL ---
st.title("💬 Sou o AIosa, seu assistente virtual...")

# Exibição do histórico
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- BARRA LATERAL (UPLOAD E CONFIGS) ---
with st.sidebar:
    st.subheader("Análise de Dados")
    arquivo_subido = st.file_uploader("Envie sua planilha (CSV ou XLSX)", type=["csv", "xlsx"])
    
    contexto_arquivo = ""
    if arquivo_subido is not None:
        try:
            if arquivo_subido.name.endswith('.csv'):
                df_analise = pd.read_csv(arquivo_subido)
            else:
                df_analise = pd.read_excel(arquivo_subido)
            
            st.success("Arquivo carregado com sucesso!")
            st.write(f"Linhas: {df_analise.shape[0]} | Colunas: {df_analise.shape[1]}")
            
            # Criar um resumo dos dados para a IA
            resumo_dados = df_analise.head(5).to_string()
            contexto_arquivo = f"\n\nContexto do arquivo enviado:\n{resumo_dados}"
        except Exception as e:
            st.error(f"Erro ao ler arquivo: {e}")

    st.divider()
    if st.button("Limpar Chat"):
        st.session_state.messages = []
        st.rerun()

# --- INPUT DO CHAT ---
if prompt := st.chat_input("O que deseja analisar na base?"):
    # Adicionar contexto do arquivo se existir
    prompt_final = prompt + contexto_arquivo if contexto_arquivo else prompt
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Analisando dados..."):
            # Enviamos o histórico + o novo prompt com o contexto da planilha
            resposta = perguntar_ia(st.session_state.messages + [{"role": "user", "content": prompt_final}])
            
            placeholder = st.empty()
            full_res = ""
            for chunk in resposta.split(" "):
                full_res += chunk + " "
                time.sleep(0.02)
                placeholder.markdown(full_res + "▌")
            placeholder.markdown(full_res)

    # Salvamento e preservação de dados
    st.session_state.messages.append({"role": "assistant", "content": full_res})
    nova_interacao = pd.DataFrame([{
        "Data/Hora": datetime.now().strftime("%H:%M:%S"),
        "Pergunta": prompt,
        "Resposta": full_res
    }])
    st.session_state.tabela_dados = pd.concat([st.session_state.tabela_dados, nova_interacao], ignore_index=True)
