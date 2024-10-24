import os
import streamlit as st
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from PIL import Image
import time
import paho.mqtt.client as paho
import json

def on_publish(client, userdata, result):
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

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400&family=Lexend:wght@600&display=swap');
    
    .title-font {
        font-family: 'Lexend', sans-serif;
        font-size: 36px;
        text-align: center;
    }

    .subtitle-font {
        font-family: 'Inter', sans-serif;
        font-size: 24px;
        text-align: center;
    }

    .paragraph-font {
        font-family: 'Inter', sans-serif;
        font-size: 18px;
        text-align: justify;
    }
    
    .center-img {
        display: block;
        margin-left: auto;
        margin-right: auto;
        width: 200px; /* Fija el tamaño de la imagen */
    }
    
    </style>
    """, unsafe_allow_html=True)

st.markdown('<p class="title-font">Interfaces Multimodales</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle-font">CONTROL POR VOZ</p>', unsafe_allow_html=True)

image = Image.open('Yoru - Voz.png')
st.markdown(f'<img src="data:image/png;base64,{st.image(image, use_column_width=False)}" class="center-img"/>', unsafe_allow_html=True)

st.write("Toca el Botón y habla")

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
        if ( value != "") {
            document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: value}));
        }
    }
    recognition.start();
    """))

result = streamlit_bokeh_events(
    stt_button,
    events="GET_TEXT",
    key="listen",
    refresh_on_update=False,
    override_height=75,
    debounce_time=0)

if result:
    if "GET_TEXT" in result:
        st.write(result.get("GET_TEXT"))
        client1.on_publish = on_publish
        client1.connect(broker, port)
        message = json.dumps({"Act1": result.get("GET_TEXT").strip()})
        ret = client1.publish("voice_ctrl_1", message)

try:
    os.mkdir("temp")
except:
    pass
