# Streamlit app
import streamlit as st
import requests
import os

# --- Función para aplicar estilos CSS dinámicos ---
def apply_theme():
    """Inyecta CSS según el tema elegido"""
    if st.session_state.theme == "light":
        st.markdown("""
            <style>
            body {
                background-color: #FFFFFF;
                color: #000000;
            }
            .stApp {
                background-color: #FFFFFF;
                color: #000000;
            }
            .stButton>button {
                background-color: #4CAF50;
                color: white;
            }
            </style>
        """, unsafe_allow_html=True)
    else:  # Tema oscuro
        st.markdown("""
            <style>
            body {
                background-color: #0E1117;
                color: #FAFAFA;
            }
            .stApp {
                background-color: #0E1117;
                color: #FAFAFA;
            }
            .stButton>button {
                background-color: #4CAF50;
                color: white;
            }
            </style>
        """, unsafe_allow_html=True)

# --- Función para alternar tema ---
def toggle_theme():
    """Alterna entre modo claro y oscuro y fuerza rerun"""
    st.session_state.theme = "dark" if st.session_state.theme == "light" else "light"
    st.rerun()

# --- Configuración de la página ---
st.set_page_config(
    page_title="🤖 Mi Chatbot Básico",
    layout="centered",
    initial_sidebar_state="auto",
    menu_items=None
)

# Inicializamos tema por defecto
if "theme" not in st.session_state:
    st.session_state.theme = "light"

# Aplicar el tema actual
apply_theme()

# --- Título ---
st.title("🤖 Mi Chatbot Básico")

# --- Botón para alternar tema ---
if st.button("✨ Toggle Dark/Light Mode"):
    toggle_theme()

# Definimos la URL de tu backend FastAPI
BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")
API_ENDPOINT = f"{BACKEND_URL}/ask"

# Inicialización del historial de mensajes
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "¡Hola! Soy un chatbot. ¿En qué puedo ayudarte hoy?"}
    ]

# Mostrar mensajes previos
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Entrada del usuario
if prompt := st.chat_input("Escribe tu mensaje aquí..."):

    # Añadir mensaje del usuario
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Mostrar mensaje del usuario
    with st.chat_message("user"):
        st.markdown(prompt)

    # Respuesta del asistente
    with st.chat_message("assistant"):
        with st.spinner("Pensando..."):
            try:
                response = requests.post(API_ENDPOINT, json={"question": prompt}, timeout=60)
                response.raise_for_status()

                api_response_data = response.json()

                # Extraemos la pregunta original y los chunks
                original_question = api_response_data.get("question", "Pregunta desconocida")
                retrieved_chunks = api_response_data.get("retrieved_chunks", [])
                backend_error = api_response_data.get("error") # Por si hay un error del backend

                # --- Construimos el contenido a mostrar en la burbuja del chatbot ---
                display_content = ""

                if backend_error:
                    display_content += f"**¡Error del Backend!** {backend_error}\n\n"

                display_content += f"**Tu pregunta original:**\n> _{original_question}_\n\n"

                if retrieved_chunks:
                    display_content += "**Chunks recuperados:**\n"
                    for i, chunk in enumerate(retrieved_chunks):
                        display_content += f"- **Chunk {i+1}:** `{chunk}`\n" # Formato Markdown para los chunks
                else:
                    display_content += "*No se recuperaron chunks para esta pregunta.*"


                # Mostramos el contenido combinado
                st.markdown(display_content)

            except requests.exceptions.ConnectionError:
                display_content = "Lo siento, no pude conectar con el servidor backend. Asegúrate de que está funcionando."
                st.error(display_content)
            except requests.exceptions.Timeout:
                display_content = "La conexión al backend tardó demasiado en responder."
                st.error(display_content)
            except requests.exceptions.RequestException as e:
                display_content = f"Error al interactuar con el backend: {e}. Revisa los logs del backend."
                st.error(display_content)
            except Exception as e:
                display_content = f"Ocurrió un error inesperado en el frontend: {e}"
                st.error(display_content)

        # Guardamos el contenido completo en el historial del chat
        st.session_state.messages.append({"role": "assistant", "content": display_content})
