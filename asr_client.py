import streamlit as st
import google.generativeai as genai
import time
import os

def transcribe_media(media_file):
    if media_file is None:
        return ""
    
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        
        # Extracción dinámica de la extensión para evitar errores de decodificación
        file_extension = media_file.name.split(".")[-1]
        file_path = f"temp_media_file.{file_extension}"
        
        with open(file_path, "wb") as f:
            f.write(media_file.getbuffer())
        
        media_upload = genai.upload_file(path=file_path, mime_type=media_file.type)
        
        while media_upload.state.name == "PROCESSING":
            time.sleep(2)
            media_upload = genai.get_file(media_upload.name)
            
        if media_upload.state.name == "FAILED":
            return "Error: Falla crítica en el procesamiento del archivo multimedia."
            
        model = genai.GenerativeModel('models/gemini-2.5-flash')
        
        # Directiva adaptada para inferencia multimodal (Audio + Fotogramas)
        response = model.generate_content([
            "Analiza este archivo multimedia. Transcribe el contenido hablado íntegramente. Si es un archivo de video, extrae e integra al texto cualquier información visual clínica relevante (diagramas, diapositivas, esquemas anatómicos). Mantén estricta precisión técnica médica.",
            media_upload
        ])
        
        genai.delete_file(media_upload.name)
        if os.path.exists(file_path):
            os.remove(file_path)
            
        return response.text
        
    except Exception as e:
        return f"Error técnico en el motor de extracción: {str(e)}"
