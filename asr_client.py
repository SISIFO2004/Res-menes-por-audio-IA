import streamlit as st
import google.generativeai as genai
import time
import os

def transcribe_audio(audio_file):
    if audio_file is None:
        return ""
    
    try:
        # Configuramos Gemini con tu llave gratuita
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        
        # Creamos un archivo temporal local para subirlo a Google
        file_path = "temp_audio_file"
        with open(file_path, "wb") as f:
            f.write(audio_file.getbuffer())
        
        # Subimos el audio a la API de Google
        audio_upload = genai.upload_file(path=file_path, mime_type=audio_file.type)
        
        # Esperamos a que Google procese el audio
        while audio_upload.state.name == "PROCESSING":
            time.sleep(2)
            audio_upload = genai.get_file(audio_upload.name)
            
        if audio_upload.state.name == "FAILED":
            return "Error: El procesamiento del audio en Google falló."
            
        # Usamos Gemini 1.5 Flash (el modelo rápido y gratis) para transcribir
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content([
            "Por favor, transcribe este audio íntegramente en español. Si es una clase médica, asegúrate de escribir correctamente los términos técnicos.",
            audio_upload
        ])
        
        # Limpieza: Borramos el archivo de los servidores de Google y el temporal
        genai.delete_file(audio_upload.name)
        if os.path.exists(file_path):
            os.remove(file_path)
            
        return response.text
        
    except Exception as e:
        return f"Error en el motor de audio Gemini: {str(e)}"
