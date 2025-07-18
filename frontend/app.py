# Streamlit app (ARCHIVO DE PRUEBA, A MODIFICAR)

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

# Configuración de la API key de OpenAI
openai.api_key = st.secrets["OPENAI_API_KEY"]

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
            response_stream = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                stream=True,
            )
            response = st.write_stream(response_stream)

    # Guardar respuesta del asistente
    st.session_state.messages.append({"role": "assistant", "content": response})
