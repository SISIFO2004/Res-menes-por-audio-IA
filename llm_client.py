import google.generativeai as genai
import streamlit as st

def process_with_llm(texto_audio=None, texto_doc=None):
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    
    # Motor confirmado
    model = genai.GenerativeModel('models/gemini-2.5-flash')
    
    # Directiva estricta que anula el comportamiento conversacional
    prompt_base = """Actúa como un especialista médico riguroso. Tu única directiva es analizar la información proporcionada y generar un resumen clínico estructurado, objetivo y con alto rigor científico. NO saludes. NO pidas información adicional. NO utilices analogías. Genera directamente el reporte en formato Markdown con viñetas.

    DATOS CLÍNICOS PARA ANÁLISIS EXCLUSIVO:
    """
    
    # Concatenación de matrices de datos
    if texto_audio and texto_doc:
        prompt_final = prompt_base + f"\n[TRANSCRIPCIÓN DE PONENCIA]:\n{texto_audio}\n\n[LITERATURA DE REFERENCIA]:\n{texto_doc}"
    elif texto_audio:
        prompt_final = prompt_base + f"\n[TRANSCRIPCIÓN DE PONENCIA]:\n{texto_audio}"
    elif texto_doc:
        prompt_final = prompt_base + f"\n[LITERATURA DE REFERENCIA]:\n{texto_doc}"
    else:
        return "Error: Ausencia de matrices de datos para el análisis."

    try:
        response = model.generate_content(prompt_final)
        return response.text
    except Exception as e:
        return f"Error técnico en el motor LLM: {str(e)}"
