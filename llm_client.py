import google.generativeai as genai
import streamlit as st
from prompts import PROMPT_INTEGRADO, PROMPT_AUDIO, PROMPT_DOCUMENTO

def process_with_llm(texto_audio=None, texto_doc=None):
    """
    Coordina la inferencia semántica basada en las fuentes disponibles.
    """
    # Configuración de la API Key desde Secrets
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    
    # Selección del modelo estable para la capa gratuita
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # Lógica de construcción de prompt según disponibilidad de datos
    if texto_audio and texto_doc:
        prompt_final = PROMPT_INTEGRADO.format(transcripcion=texto_audio, documento=texto_doc)
    elif texto_audio:
        prompt_final = PROMPT_AUDIO.format(transcripcion=texto_audio)
    elif texto_doc:
        prompt_final = PROMPT_DOCUMENTO.format(documento=texto_doc)
    else:
        return "Error: No se proporcionaron fuentes de datos válidas para el análisis."

    try:
        # Ejecución de la generación de contenido
        response = model.generate_content(prompt_final)
        return response.text
    except Exception as e:
        return f"Error crítico en el motor LLM: {str(e)}"
