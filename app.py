import streamlit as st
import requests
import os

st.set_page_config(page_title="Assistente IA", page_icon="🤖", layout="centered")

st.title("Assistente IA Online")

# Token vindo do Streamlit Secrets
HF_TOKEN = os.getenv("HF_TOKEN")

API_URL = "https://api-inference.huggingface.co/models/google/flan-t5-base"

headers = {
    "Authorization": f"Bearer {HF_TOKEN}"
}


def perguntar_ia(pergunta):
    try:
        response = requests.post(
            API_URL,
            headers=headers,
            json={"inputs": pergunta},
            timeout=30,
        )

        if response.status_code == 200:
            resultado = response.json()
            return resultado[0]["generated_text"]
        else:
            return f"Erro {response.status_code}: {response.text}"

    except Exception as e:
        return f"Erro de conexão: {e}"


# Interface simples
pergunta = st.text_input("Digite sua pergunta:")

if pergunta:
    with st.spinner("Pensando..."):
        resposta = perguntar_ia(pergunta)
        st.write(resposta)
