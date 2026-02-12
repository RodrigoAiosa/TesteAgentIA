import streamlit as st
import requests
import os

st.title("Assistente IA Online")

HF_TOKEN = os.getenv("HF_TOKEN")

API_URL = "https://api-inference.huggingface.co/models/google/flan-t5-base"

headers = {
    "Authorization": f"Bearer {HF_TOKEN}"
}

def perguntar_ia(pergunta):
    payload = {"inputs": pergunta}
    response = requests.post(API_URL, headers=headers, json=payload)

    if response.status_code == 200:
        return response.json()[0]["generated_text"]
    else:
        return f"Erro {response.status_code}: {response.text}"

pergunta = st.text_input("Digite sua pergunta:")

if pergunta:
    resposta = perguntar_ia(pergunta)
    st.write(resposta)
