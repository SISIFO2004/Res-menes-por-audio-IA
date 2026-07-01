import streamlit as st
import google.generativeai as genai
import time
import os

def transcribe_media(media_file):
    if media_file is None:
        return ""
    
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        
        # Extracción dinámica de la extensión
        file_extension = media_file.name.split(".")[-1]
        file_path = f"temp_media_file.{file_extension}"
        
        with open(file_path, "wb") as f:
            f.write(media_file.getbuffer())
        
        media_upload = genai.upload_file(path=file_path, mime_type=media_file.type)
        
        # Polling relajado para darle tiempo a Google de procesar la hora entera de audio
        while media_upload.state.name == "PROCESSING":
            time.sleep(20) 
            media_upload = genai.get_file(media_upload.name)
            
        if media_upload.state.name == "FAILED":
            return "Error: Falla crítica en el procesamiento del archivo multimedia en la nube."
            
        model = genai.GenerativeModel('models/gemini-2.5-flash')
        
        # =========================================================
        # SISTEMA DE AUTO-RECUPERACIÓN ANTI ERROR 429
        # =========================================================
        max_intentos = 3
        for intento in range(max_intentos):
            try:
                time.sleep(5) # Respiro base antes de pedir la inferencia
                
                # Solicitud de transcripción
                response = model.generate_content([
                    "Analiza este archivo multimedia. Transcribe el contenido hablado íntegramente. Si es un archivo de video, extrae e integra al texto cualquier información visual clínica relevante (diagramas, diapositivas, esquemas anatómicos). Mantén estricta precisión técnica médica.",
                    media_upload
                ])
                break # Si el análisis es exitoso, rompemos el bucle y avanzamos
                
            except Exception as e:
                # Si Google nos golpea con el límite de cuota (Error 429)
                if "429" in str(e) or "Quota" in str(e):
                    if intento < max_intentos - 1:
                        # Mandamos una pequeña notificación a la pantalla para que sepas qué pasa
                        st.toast(f"⏳ Google saturado. Activando pausa automática de 60s (Intento {intento+1}/{max_intentos})...", icon="⚠️")
                        time.sleep(60) # Congelamos el código 1 minuto exacto
                    else:
                        raise e # Si falló 3 veces seguidas, dejamos que muestre el error
                else:
                    raise e # Si es un error diferente, lo reporta de inmediato
        
        # Limpieza de basura en la nube y en tu disco
        genai.delete_file(media_upload.name)
        if os.path.exists(file_path):
            os.remove(file_path)
            
        return response.text
        
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "Quota" in error_msg:
            return "⚠️ **Límite de cuota superado.** El audio es demasiado masivo y los reintentos automáticos se agotaron. Deja descansar la API por 5 minutos."
        return f"Error técnico en el motor de extracción: {error_msg}"
