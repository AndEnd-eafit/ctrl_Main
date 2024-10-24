import os
import streamlit as st
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from PIL import Image
import time
import glob
import paho.mqtt.client as paho
import json
from gtts import gTTS
from googletrans import Translator

def on_publish(client, userdata, result):  # Callback para la publicación
    print("El dato ha sido publicado \n")
    pass

def on_message(client, userdata, message):
    global message_received
    time.sleep(2)
    message_received = str(message.payload.decode("utf-8"))
    st.write(message_received)

broker = "broker.mqttdashboard.com"
port = 1883
client1 = paho.Client("GIT-Yoru")
client1.on_message = on_message

# Añadir las fuentes personalizadas y estilos
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400&family=Lexend:wght@600&display=swap');

    .title-font {
        font-family: 'Lexend', sans-serif;
        font-size: 36px;
        text-align: left;
    }

    .subtitle-font {
        font-family: 'Inter', sans-serif;
        font-size: 24px;
        text-align: left;
    }

    .paragraph-font {
        font-family: 'Inter', sans-serif;
        font-size: 18px;
        text-align: left;
    }
    </style>
    """, unsafe_allow_html=True)

# Título y subtítulo con la nueva tipografía
st.markdown('<p class="title-font">Interfaces Multimodales</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle-font">CONTROL POR VOZ</p>', unsafe_allow_html=True)

# Cargar imagen
image = Image.open('Yoru - Voz.png')
st.image(image, width=200)

# Texto de instrucciones
st.write("Toca el Botón y habla")

# Botón para iniciar el reconocimiento de voz
stt_button = Button(label=" Inicio ", width=200)
stt_button.js_on_event("button_click", CustomJS(code="""
    var recognition = new webkitSpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
 
    recognition.onresult = function (e) {
        var value = "";
        for (var i = e.resultIndex; i < e.results.length; ++i) {
            if (e.results[i].isFinal) {
                value += e.results[i][0].transcript;
            }
        }
        if (value != "") {
            document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: value}));
        }
    }
    recognition.start();
    """))

# Escuchar el evento de la voz
result = streamlit_bokeh_events(
    stt_button,
    events="GET_TEXT",
    key="listen",
    refresh_on_update=False,
    override_height=75,
    debounce_time=0)

# Publicar el mensaje de voz recibido a través de MQTT
if result:
    if "GET_TEXT" in result:
        st.write(result.get("GET_TEXT"))
        client1.on_publish = on_publish
        client1.connect(broker, port)
        message = json.dumps({"Act1": result.get("GET_TEXT").strip()})
        ret = client1.publish("voice_ctrl_1", message)

# Crear el directorio temporal si no existe
try:
    os.mkdir("temp")
except:
    pass
