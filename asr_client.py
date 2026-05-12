import streamlit as st
import google.generativeai as genai
import time
import os

def transcribe_audio(audio_file):
    if audio_file is None:
        return ""
    
    try:
        # Autenticación de la API
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        
        # Generación de archivo temporal para la ingesta
        file_path = "temp_audio_file"
        with open(file_path, "wb") as f:
            f.write(audio_file.getbuffer())
        
        # Carga del archivo al servidor de Google
        audio_upload = genai.upload_file(path=file_path, mime_type=audio_file.type)
        
        # Monitoreo de estado
        while audio_upload.state.name == "PROCESSING":
            time.sleep(2)
            audio_upload = genai.get_file(audio_upload.name)
            
        if audio_upload.state.name == "FAILED":
            return "Error: Falla crítica en el procesamiento acústico."
            
        # Asignación del modelo estático (Hardcoded version hash)
        model = genai.GenerativeModel('gemini-1.5-flash-001')
        
        # Ejecución de inferencia
        response = model.generate_content([
            "Transcribe este audio íntegramente. Mantén la precisión técnica médica.",
            audio_upload
        ])
        
        # Limpieza de memoria y servidor
        genai.delete_file(audio_upload.name)
        if os.path.exists(file_path):
            os.remove(file_path)
            
        return response.text
        
    except Exception as e:
        return f"Error técnico en el motor ASR: {str(e)}"
