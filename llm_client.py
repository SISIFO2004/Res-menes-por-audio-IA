import google.generativeai as genai
import streamlit as st

def process_with_llm(texto_media=None, texto_doc=None):
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    
    model = genai.GenerativeModel('models/gemini-2.5-flash')
    
    prompt_base = """Actúa como un especialista médico riguroso. Tu única directiva es analizar la información proporcionada y generar un resumen clínico estructurado, objetivo y con alto rigor científico. NO saludes. NO pidas información adicional. NO utilices analogías. Genera directamente el reporte en formato Markdown con viñetas.

    DATOS CLÍNICOS PARA ANÁLISIS EXCLUSIVO:
    """
    
    if texto_media and texto_doc:
        prompt_final = prompt_base + f"\n[EXTRACCIÓN MULTIMEDIA DE LA PONENCIA]:\n{texto_media}\n\n[LITERATURA DE REFERENCIA]:\n{texto_doc}"
    elif texto_media:
        prompt_final = prompt_base + f"\n[EXTRACCIÓN MULTIMEDIA DE LA PONENCIA]:\n{texto_media}"
    elif texto_doc:
        prompt_final = prompt_base + f"\n[LITERATURA DE REFERENCIA]:\n{texto_doc}"
    else:
        return "Error: Ausencia de matrices de datos para el análisis."

    try:
        response = model.generate_content(prompt_final)
        return response.text
    except Exception as e:
        return f"Error técnico en el motor LLM: {str(e)}"
