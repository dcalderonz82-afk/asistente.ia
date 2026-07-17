import streamlit as st
from google import genai
from google.genai import types

# 1. Configuración de la página web
st.set_page_config(page_title="Mi Chatbot con Memoria", page_icon="💬", layout="centered")

st.title("💬 Mi Chatbot Inteligente")
st.write("Pregúntame lo que sea. ¡Ahora recuerdo todo lo que me dices en esta sesión!")

# Botón para limpiar el historial y empezar de nuevo
if st.button("Limpiar conversación 🔄"):
    st.session_state.messages = []
    st.rerun()

# 2. Conexión segura con la API Key
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=api_key)
except Exception:
    st.error("⚠️ Configura la variable 'GEMINI_API_KEY' en la configuración de Secrets de Streamlit.")
    st.stop()

# 3. Inicializar la "memoria" si es la primera vez que entramos
if "messages" not in st.session_state:
    st.session_state.messages = []

# 4. Mostrar en pantalla todos los mensajes que ya están guardados en la memoria
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5. Capturar el nuevo mensaje del usuario (usando la elegante barra de chat inferior)
if prompt := st.chat_input("Escribe un mensaje aquí..."):
    
    # Mostramos el mensaje del usuario de inmediato en la pantalla
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Guardamos el mensaje en nuestra "caja fuerte" de memoria
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 6. Preparar el historial en el formato exacto que Gemini necesita recibir
    historial_para_api = []
    for msg in st.session_state.messages:
        # Gemini espera que el rol del bot se llame 'model' en lugar de 'assistant'
        role_api = "user" if msg["role"] == "user" else "model"
        
        historial_para_api.append(
            types.Content(
                role=role_api,
                parts=[types.Part.from_text(text=msg["content"])]
            )
        )

    # 7. Solicitar la respuesta enviando el historial de chat completo
    with st.chat_message("assistant"):
        with st.spinner("Pensando..."):
            try:
                response = client.models.generate_content(
                    model='gemini-2.0-flash',
                    contents=historial_para_api, # <--- Enviamos TODO el historial acumulado
                    config=types.GenerateContentConfig(
                        system_instruction="Eres un asistente de IA muy amigable, divertido y conversacional. Saluda cordialmente."
                    )
                )
                
                # Mostramos la respuesta del bot en la pantalla
                st.markdown(response.text)
                
                # Guardamos la respuesta del bot en la "caja fuerte" de memoria
                st.session_state.messages.append({"role": "assistant", "content": response.text})
                
            except Exception as e:
                st.error(f"Ocurrió un error: {e}")
