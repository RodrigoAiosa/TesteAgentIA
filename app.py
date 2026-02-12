import streamlit as st
import requests
import os
import pandas as pd
from datetime import datetime

# Configuração da página
st.set_page_config(page_title="Assistente IA", page_icon="🤖")
st.title("Assistente IA Online")

# --- CONFIGURAÇÕES DE API ---
HF_TOKEN = os.getenv("HF_TOKEN")
# Alterado para um modelo estável na API gratuita para evitar o Erro 400
API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.3"

headers = {
    "Authorization": f"Bearer {HF_TOKEN}",
    "Content-Type": "application/json",
}

# --- PERSISTÊNCIA DE DADOS ---
# Inicializa a tabela no estado da sessão para preservar os dados existentes
if "tabela_dados" not in st.session_state:
    st.session_state.tabela_dados = pd.DataFrame(columns=["Data/Hora", "Pergunta", "Resposta"])

def perguntar_ia(pergunta):
    # Formato de payload compatível com a Inference API
    payload = {
        "inputs": f"<s>[INST] {pergunta} [/INST]",
        "parameters": {
            "max_new_tokens": 300,
            "temperature": 0.7,
        },
        "options": {"wait_for_model": True}
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            # Ajuste para extrair o texto corretamente do retorno da API
            if isinstance(data, list):
                return data[0].get("generated_text", "Erro ao processar resposta.")
            return data.get("generated_text", "Erro ao processar resposta.")
        else:
            return f"Erro {response.status_code}: {response.text}"
    except Exception as e:
        return f"Erro de conexão: {str(e)}"

# --- INTERFACE ---
pergunta = st.text_input("Digite sua pergunta:")

if pergunta:
    with st.spinner("Pensando..."):
        resposta = perguntar_ia(pergunta)
        
        # Salva novos dados preservando os existentes na tabela
        nova_entrada = pd.DataFrame([{
            "Data/Hora": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "Pergunta": pergunta,
            "Resposta": resposta
        }])
        
        # Concatena a nova linha à tabela salva na sessão
        st.session_state.tabela_dados = pd.concat([st.session_state.tabela_dados, nova_entrada], ignore_index=True)
        
        st.markdown("### Resposta Atual:")
        st.write(resposta)

# --- EXIBIÇÃO DA TABELA ---
if not st.session_state.tabela_dados.empty:
    st.divider()
    st.subheader("Histórico de Dados Salvos")
    # Exibe a tabela com todo o histórico da sessão
    st.dataframe(st.session_state.tabela_dados, use_container_width=True)
    
    # Botão para exportar os dados acumulados
    csv = st.session_state.tabela_dados.to_csv(index=False).encode('utf-8')
    st.download_button("Baixar Dados (CSV)", csv, "historico_ia.csv", "text/csv")
