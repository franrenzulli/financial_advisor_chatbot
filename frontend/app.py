# Streamlit app (app.py)
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
# Aquí almacenamos el historial que se muestra Y se envía al backend
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

    # Añadir mensaje del usuario al historial para mostrarlo y para la próxima petición
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Mostrar mensaje del usuario inmediatamente
    with st.chat_message("user"):
        st.markdown(prompt)

    # Preparar el historial para enviar al backend
    # Aquí puedes decidir cuántos turnos quieres enviar.
    # Por ejemplo, los últimos 5 turnos (10 mensajes, 5 del user y 5 del assistant)
    # o toda la conversación si no es muy larga.
    # Es crucial que el historial no contenga el prompt actual que estamos enviando.
    # st.session_state.messages ya incluye el prompt actual, así que lo enviamos tal cual.
    # Sin embargo, para la API de OpenAI, solo queremos los mensajes de 'role' y 'content'.
    
    # Creamos una lista de mensajes limpios para el LLM.
    # Excluimos el mensaje de bienvenida inicial si no queremos que influya en el contexto.
    # Y nos aseguramos de que cada mensaje tenga solo 'role' y 'content'.
    chat_history_for_llm = []
    # Iteramos desde el segundo mensaje si el primero es el de bienvenida fijo
    start_index = 1 if st.session_state.messages[0]["role"] == "assistant" and \
                        "¡Hola!" in st.session_state.messages[0]["content"] else 0

    for msg in st.session_state.messages[start_index:-1]: # Excluimos el último mensaje que es el 'prompt' actual
        chat_history_for_llm.append({"role": msg["role"], "content": msg["content"]})
    
    # Puedes limitar la longitud del historial para no exceder los límites de tokens del LLM
    # Por ejemplo, los últimos 10 mensajes (5 turnos completos):
    # chat_history_for_llm = chat_history_for_llm[-10:] 

    # Respuesta del asistente
    with st.chat_message("assistant"):
        with st.spinner("Pensando..."):
            try:
                # Realizar la llamada POST a tu API de FastAPI
                # Enviamos la pregunta y el historial en formato JSON
                response = requests.post(
                    API_ENDPOINT,
                    json={
                        "question": prompt,
                        "chat_history": chat_history_for_llm # <-- ¡Aquí enviamos el historial!
                    },
                    timeout=60
                )
                response.raise_for_status()

                api_response_data = response.json()

                # Extraemos todo lo que viene del backend
                original_question = api_response_data.get("question", "Pregunta desconocida")
                llm_answer = api_response_data.get("answer", "Error: No se pudo obtener la respuesta del asistente.")
                retrieved_chunks = api_response_data.get("retrieved_chunks", [])
                backend_error = api_response_data.get("error")

                # --- Construimos el contenido final a mostrar en la burbuja del chatbot ---
                display_content = ""

                if backend_error:
                    display_content += f"**¡Error del Backend!** {backend_error}\n\n"

                display_content += f"""
                **Tu pregunta original:**
                > _{original_question}_

                ---

                **Respuesta del asistente:**
                {llm_answer}
                """

                if retrieved_chunks:
                    chunks_for_expander = ""
                    for i, chunk in enumerate(retrieved_chunks):
                        chunks_for_expander += f"**Chunk {i+1}:**\n```\n{chunk}\n```\n\n"

                    st.markdown(display_content)
                    with st.expander("Ver fuentes (chunks recuperados)"):
                        st.markdown(chunks_for_expander)
                else:
                    st.markdown(display_content + "\n\n*No se recuperaron fuentes para esta respuesta.*")

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

        # Guardar la respuesta completa en el historial de mensajes de Streamlit
        # (para que se muestre en la UI y sea parte del contexto futuro)
        st.session_state.messages.append({"role": "assistant", "content": display_content})
