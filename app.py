import os
import base64
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
from streamlit_mic_recorder import mic_recorder

load_dotenv()
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "texto_audio" not in st.session_state:
    st.session_state.texto_audio = ""

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

st.set_page_config(
    page_title="Tomi",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Hola Amiguito! Soy Tomi")
st.subheader("Tu compañero de estudio")

if st.button("🗑️ Nueva conversación"):

    st.session_state.chat_history = []
    st.session_state.texto_audio = ""

    st.rerun()

st.write("""
Podés:

📷 Subir una foto

📝 Escribir una pregunta

🎤 Hablarme

Y te voy a ayudar a estudiar.
""")

pregunta = st.text_area(
    "¿Qué estás estudiando hoy, Joaqui?",
    placeholder="Por ejemplo: Segunda Guerra Mundial"
)

uploaded_file = st.file_uploader(
    "📷 Subí una foto",
    type=["jpg", "jpeg", "png"]
)

st.subheader("🎤 Hablar con Tomi")

audio_grabado = mic_recorder(
    start_prompt="🎤 Empezar a hablar",
    stop_prompt="⏹️ Terminar",
    just_once=True,
    use_container_width=True
)

if "texto_audio" not in st.session_state:
    st.session_state.texto_audio = ""

if audio_grabado:

    with open("audio_joaqui.wav", "wb") as f:
        f.write(audio_grabado["bytes"])

    with open("audio_joaqui.wav", "rb") as audio:

        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio
        )

    st.session_state.texto_audio = transcript.text



texto_audio = st.session_state.texto_audio

if uploaded_file:
    st.image(uploaded_file)

ejecutar = False

if pregunta or uploaded_file:
    ejecutar = st.button("🧠 Ayudame a estudiar")

if texto_audio:
    ejecutar = True

if ejecutar:

    if not pregunta and not uploaded_file and not texto_audio:

        st.warning(
            "Escribí algo, hablame o subí una foto."
        )

        st.stop()

    with st.spinner("Tomi está pensando..."):

        mensajes = [
            {
                "role": "system",
                "content": """
Sos Tomi.

Sos el compañero de estudio de Joaquín.

Joaquín tiene 13 años y dislexia.

Tu trabajo principal es ayudarlo a entender y darle confianza.

Hablás como un argentino.

Usás voseo.

Usás expresiones como:
- contame
- querés
- vamos de a poco
- probemos otra forma

Nunca usás expresiones de España.

Nunca decís:
- dímelo
- cuéntame
- vale
- vosotros

A veces podés llamarlo:
- Joaqui
- Joaco
- Amiguito

No abuses de esos apodos.

Intentás transmitir tranquilidad.

Tu tono se parece más al de un familiar que ayuda a estudiar.

Nunca apurás a Joaquín.

Si nota frustración:
- bajás el ritmo
- simplificás
- reforzás la confianza

Explicás con frases cortas.

Transformás Historia en relatos fáciles de recordar.

Si Joaquín pone solo un tema:

Ejemplo:
- Segunda Guerra Mundial
- Revolución Francesa

No le preguntes qué quiere saber.

Explicalo directamente.

Siempre:

1. Hacé un resumen.
2. Explicalo fácil.
3. Destacá lo más importante.
4. Terminá con tres preguntas.
"""
            }
        ]
        mensajes.extend(
    st.session_state.chat_history
)

        if uploaded_file:

            image_bytes = uploaded_file.read()

            base64_image = base64.b64encode(
                image_bytes
            ).decode("utf-8")

            texto_usuario = ""

            if pregunta:
                texto_usuario += pregunta

            if texto_audio:
                texto_usuario += "\n" + texto_audio

            if not texto_usuario:
                texto_usuario = "Leé esta página y ayudame a entenderla."

            mensajes.append(
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": texto_usuario
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            )

        else:

            contenido_usuario = ""

            if pregunta:
                contenido_usuario += pregunta

            if texto_audio:
                contenido_usuario += "\n" + texto_audio

            mensajes.append(
                {
                    "role": "user",
                    "content": contenido_usuario
                }
            )

        respuesta = client.chat.completions.create(
            model="gpt-4o",
            messages=mensajes
        )

        texto_tomi = respuesta.choices[0].message.content

        contenido_memoria = ""

        if pregunta:
            contenido_memoria += pregunta

        if texto_audio:
            contenido_memoria += "\n" + texto_audio

        st.session_state.chat_history.append(
            {
                "role": "user",
                "content": contenido_memoria
            }
        )

        st.session_state.chat_history.append(
            {
                "role": "assistant",
                "content": texto_tomi
            }
        )

        st.success("✅ Tomi respondió")
        st.markdown(texto_tomi)
        st.session_state.ultima_respuesta = texto_tomi
        
        st.session_state.texto_audio = ""

        try:

            speech_file_path = Path(
                "tomi_audio.mp3"
            )

            with client.audio.speech.with_streaming_response.create(
                model="gpt-4o-mini-tts",
                voice="onyx",
                input=texto_tomi
            ) as audio_response:

                audio_response.stream_to_file(
                    speech_file_path
                )

            with open(
                "tomi_audio.mp3",
                "rb"
            ) as audio_file:

                st.audio(
                    audio_file.read()
                )

        except Exception as e:

            st.warning(
                f"No pude generar el audio: {e}"
            )
if st.button("🎓 Practicar este tema"):

    practica = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": """
Sos Tomi.

Generá ejercicios para un chico de 13 años.

Creá:

1. Dos preguntas de opción múltiple.
2. Dos verdadero o falso.
3. Una pregunta abierta.

No des las respuestas todavía.
"""
            },
            {
                "role": "user",
                "content": st.session_state.ultima_respuesta
            }
        ]
    )

    st.markdown(
        practica.choices[0].message.content
    )
