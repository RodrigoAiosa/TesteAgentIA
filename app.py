import streamlit as st
import requests
import os

st.set_page_config(page_title="Assistente IA", page_icon="🤖")
st.title("Assistente IA Online")

HF_TOKEN = os.getenv("HF_TOKEN")

API_URL = "https://router.huggingface.co/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {HF_TOKEN}",
    "Content-Type": "application/json",
}


def perguntar_ia(pergunta):
    payload = {
        "model": "microsoft/Phi-3-mini-4k-instruct",
        "messages": [
            {"role": "user", "content": pergunta}
        ],
        "max_tokens": 200,
    }

    response = requests.post(API_URL, headers=headers, json=payload)

    if response.status_code == 200:
        data = response.json()
        return data["choices"][0]["message"]["content"]
    else:
        return f"Erro {response.status_code}: {response.text}"


pergunta = st.text_input("Digite sua pergunta:")

if pergunta:
    with st.spinner("Pensando..."):
        resposta = perguntar_ia(pergunta)
        st.write(resposta)
