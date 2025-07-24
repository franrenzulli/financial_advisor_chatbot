# app.py — Frontend Streamlit más estético

import streamlit as st
import requests
import os

# --- Tema / Estilo CSS global ---
def apply_theme():
    """Aplica estilos CSS personalizados"""
    css = f"""
    <style>
    html, body, .stApp {{
        font-family: 'Segoe UI', sans-serif;
        background-color: {"#0E1117" if st.session_state.theme == "dark" else "#FFFFFF"};
        color: {"#FAFAFA" if st.session_state.theme == "dark" else "#000000"};
    }}
    .message-container {{
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
        background-color: {"#262730" if st.session_state.theme == "dark" else "#F1F1F1"};
    }}
    .user {{
        border-left: 5px solid #4CAF50;
    }}
    .assistant {{
        border-left: 5px solid #2196F3;
    }}
    .stButton>button {{
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        padding: 10px 16px;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# --- Alternar tema claro/oscuro ---
def toggle_theme():
    st.session_state.theme = "dark" if st.session_state.theme == "light" else "light"
    st.rerun()

# --- Configuración general ---
st.set_page_config(page_title="💰 Financial Chatbot", layout="centered")

if "theme" not in st.session_state:
    st.session_state.theme = "dark"

apply_theme()

st.title("💬 Asesor Financiero Chatbot")

# --- Backend ---
BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")
API_ENDPOINT = f"{BACKEND_URL}/ask"

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "¡Hola! Soy tu asesor financiero. ¿Qué deseas saber sobre el NASDAQ hoy?"}
    ]

# --- Mostrar historial de mensajes (solo UI) ---
for message in st.session_state.messages:
    role_class = "user" if message["role"] == "user" else "assistant"
    with st.container():
        st.markdown(f"""
        <div class="message-container {role_class}">
            <strong>{'🧑 Usuario' if role_class == 'user' else '🤖 Asistente'}:</strong><br>{message['content']}
        </div>
        """, unsafe_allow_html=True)

# --- Entrada del usuario ---
if prompt := st.chat_input("Haz tu pregunta..."):

    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.container():
        st.markdown(f"""
        <div class="message-container user">
            <strong>🧑 Usuario:</strong><br>{prompt}
        </div>
        """, unsafe_allow_html=True)

    # Armar historial limpio (sin el prompt actual)
    chat_history_for_llm = []
    start_index = 1 if st.session_state.messages[0]["role"] == "assistant" else 0
    for msg in st.session_state.messages[start_index:-1]:
        chat_history_for_llm.append({"role": msg["role"], "content": msg["content"]})

    # --- Llamada al backend ---
    with st.spinner("Buscando la mejor respuesta..."):
        try:
            response = requests.post(
                API_ENDPOINT,
                json={"question": prompt, "chat_history": chat_history_for_llm},
                timeout=60
            )
            response.raise_for_status()
            data = response.json()

            llm_answer = data.get("answer", "Sin respuesta.")
            retrieved_chunks = data.get("retrieved_chunks", [])

            # Mostrar respuesta
            st.markdown(f"""
            <div class="message-container assistant">
                <strong>🤖 Asistente:</strong><br>{llm_answer}
            </div>
            """, unsafe_allow_html=True)

            if retrieved_chunks:
                with st.expander("🔍 Ver fuentes utilizadas (chunks recuperados)"):
                    for i, chunk in enumerate(retrieved_chunks):
                        st.markdown(f"**Chunk {i+1}:**\n```\n{chunk}\n```")

            # Guardar en historial
            st.session_state.messages.append({"role": "assistant", "content": llm_answer})

        except Exception as e:
            st.error(f"❌ Error al conectar con el backend: {e}")
