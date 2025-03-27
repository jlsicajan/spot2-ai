import streamlit as st
import requests
from PIL import Image
import os

API_URL = "http://backend:8082/chat"

logo_path = os.path.join("assets", "spot2-logo.png")
if os.path.exists(logo_path):
    logo = Image.open(logo_path)
    st.image(logo, width=160)

st.title("Asistente Spot2")

if "session_data" not in st.session_state:
    st.session_state.session_data = {}

if "conversation" not in st.session_state:
    st.session_state.conversation = [
        {
            "role": "assistant",
            "content": "Hola. Soy el asistente de Spot2. ¿Que tipo de inmueble comercial estas buscando?",
        }
    ]

st.markdown(
    """
    <style>
        .chat-bubble {
            padding: 10px 15px;
            border-radius: 12px;
            margin: 5px 0;
            max-width: 70%;
            display: inline-block;
        }
        .user-bubble {
            background-color: #d2f8d2;
            color: black;
            text-align: right;
            align-self: flex-end;
        }
        .bot-bubble {
            background-color: #f0f0f0;
            color: black;
            text-align: left;
            align-self: flex-start;
        }
        .chat-row {
            display: flex;
            justify-content: flex-start;
        }
        .chat-row.user {
            justify-content: flex-end;
        }
    </style>
""",
    unsafe_allow_html=True,
)

for msg in st.session_state.conversation:
    if msg["role"] == "user":
        st.markdown(
            f"""
            <div class="chat-row user">
                <div class="chat-bubble user-bubble">{msg['content']}</div>
            </div>
        """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"""
            <div class="chat-row">
                <div class="chat-bubble bot-bubble">{msg['content']}</div>
            </div>
        """,
            unsafe_allow_html=True,
        )

with st.form(key="chat_form", clear_on_submit=True):
    user_input = st.text_input(
        "Tu mensaje",
        placeholder="Escribe tu mensaje y presiona Enter",
        label_visibility="collapsed",
    )
    submit = st.form_submit_button("Enviar")

if submit and user_input.strip():
    st.session_state.conversation.append({"role": "user", "content": user_input})

    payload = {"message": user_input, "session_data": st.session_state.session_data}

    try:
        response = requests.post(API_URL, json=payload)
        data = response.json()
        st.session_state.conversation.append(
            {"role": "assistant", "content": data["response"]}
        )
        st.session_state.session_data = data["session_data"]
        st.rerun()

    except Exception as e:
        st.error(f"Error: {e}")

if st.button("Reiniciar conversacion"):
    st.session_state.conversation = [
        {
            "role": "assistant",
            "content": "Hola. Soy el asistente de Spot2. ¿Que tipo de inmueble comercial estas buscando?",
        }
    ]
    st.session_state.session_data = {}
    st.rerun()
