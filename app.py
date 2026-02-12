import streamlit as st
import requests
import os

st.title("Assistente IA Online")

# Pegando token do ambiente
HF_TOKEN = os.getenv("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")

API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"

headers = {
    "Authorization": f"Bearer {HF_TOKEN}"
}

def perguntar_ia(pergunta):
    payload = {
        "inputs": pergunta,
        "parameters": {
            "max_new_tokens": 200
        }
    }
    
    response = requests.post(API_URL, headers=headers, json=payload)
    
    if response.status_code == 200:
        return response.json()[0]["generated_text"]
    else:
        return "Erro ao gerar resposta."

pergunta = st.text_input("Digite sua pergunta:")

if pergunta:
    resposta = perguntar_ia(pergunta)
    st.write(resposta)
