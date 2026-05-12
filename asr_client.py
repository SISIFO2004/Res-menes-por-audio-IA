import streamlit as st
import google.generativeai as genai
import time
import os

def transcribe_audio(audio_file):
    if audio_file is None:
        return ""
    
    try:
        # Todo este bloque ahora está correctamente indentado dentro del 'try'
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        
        file_path = "temp_audio_file"
        with open(file_path, "wb") as f:
            f.write(audio_file.getbuffer())
        
        audio_upload = genai.upload_file(path=file_path, mime_type=audio_file.type)
        
        while audio_upload.state.name == "PROCESSING":
            time.sleep(2)
            audio_upload = genai.get_file(audio_upload.name)
            
        if audio_upload.state.name == "FAILED":
            return "Error: Falla en el procesamiento del audio."
            
        model = genai.GenerativeModel(model_name='gemini-1.5-flash')
        
        response = model.generate_content([
            "Transcribe este audio íntegramente. Mantén la precisión técnica médica.",
            audio_upload
        ])
        
        genai.delete_file(audio_upload.name)
        if os.path.exists(file_path):
            os.remove(file_path)
            
        return response.text
        
    except Exception as e:
        # El bloque except se alinea con el try
        return f"Error en el motor de audio Gemini: {str(e)}"
        
        genai.delete_file(audio_upload.name)
        if os.path.exists(file_path):
            os.remove(file_path)
            
        return response.text
        
    except Exception as e:
        return f"Error en el motor de audio Gemini: {str(e)}"
