import streamlit as st
from openai import OpenAI

def transcribe_audio(audio_file) -> str:
    """
    Motor de transcripción acústica.
    Toma el archivo binario en RAM (Streamlit UploadedFile) y lo procesa mediante Whisper.
    """
    if audio_file is None:
        return ""

    try:
        # Inicialización del cliente extrayendo la API Key de las variables seguras
        client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

        # Inferencia acústica
        response = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            response_format="text",
            # Se fija el idioma en español para reducir la tasa de error (WER)
            language="es"
        )
        
        return response
        
    except KeyError:
        return "Error de Configuración: No se encontró OPENAI_API_KEY en st.secrets."
    except Exception as e:
        return f"Error crítico en el motor ASR: {str(e)}"
