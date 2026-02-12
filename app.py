import streamlit as st
import requests
import os

st.set_page_config(page_title="Assistente IA", page_icon="🤖")

st.title("Assistente IA Online")

HF_TOKEN = os.getenv("HF_TOKEN")

API_URL = "https://router.huggingface.co/hf-inference/models/google/flan-t5-base"

headers = {
    "Authorization": f"Bearer {HF_TOKEN}",
    "Content-Type": "application/json"
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


pergunta = st.text_input("Digite sua pergunta:")

if pergunta:
    with st.spinner("Pensando..."):
        st.write(perguntar_ia(pergunta))
