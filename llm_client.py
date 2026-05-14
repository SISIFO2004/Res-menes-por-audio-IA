import google.generativeai as genai
import streamlit as st
import time

def process_with_llm(texto_media=None, texto_doc=None):
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('models/gemini-2.5-flash')
    
    prompt_base = """Actúa como un especialista médico riguroso. Tu única directiva es analizar la información proporcionada y generar un resumen clínico estructurado, objetivo y con alto rigor científico. NO saludes. NO pidas información adicional. NO utilices analogías. Genera directamente el reporte en formato Markdown con viñetas.

    DATOS CLÍNICOS PARA ANÁLISIS EXCLUSIVO:
    """
    
    if not texto_media and not texto_doc:
        return "Error: Ausencia de matrices de datos para el análisis."

    try:
        # Algoritmo de Bifurcación de Carga
        # Umbral configurado a 30,000 caracteres (aprox. 30-40 minutos de clase)
        if texto_media and len(texto_media) > 30000:
            
            # Cálculo del punto de corte para no fragmentar oraciones clínicas
            mitad = len(texto_media) // 2
            punto_corte = texto_media.find('\n\n', mitad)
            if punto_corte == -1: 
                punto_corte = texto_media.find('\n', mitad)
            if punto_corte == -1: 
                punto_corte = mitad
                
            parte_1 = texto_media[:punto_corte]
            parte_2 = texto_media[punto_corte:]
            
            # Ejecución del Lote 1
            prompt_1 = prompt_base + f"\n[PARTE 1 - EXTRACCIÓN MULTIMEDIA]:\n{parte_1}\n\n[LITERATURA DE REFERENCIA]:\n{texto_doc if texto_doc else 'No provista.'}"
            response_1 = model.generate_content(prompt_1)
            
            # Pausa estricta de 35 segundos para purgar la cuota de la API
            time.sleep(35) 
            
            # Ejecución del Lote 2
            prompt_2 = prompt_base + f"\n[PARTE 2 - EXTRACCIÓN MULTIMEDIA]:\n{parte_2}\n\n[LITERATURA DE REFERENCIA]:\n{texto_doc if texto_doc else 'No provista.'}"
            response_2 = model.generate_content(prompt_2)
            
            # Concatenación de resultados estructurados
            return f"### 📊 FASE 1: SÍNTESIS CLÍNICA\n\n{response_1.text}\n\n---\n\n### 📊 FASE 2: SÍNTESIS CLÍNICA\n\n{response_2.text}"
        
        else:
            # Ejecución estándar para archivos dentro del umbral seguro de tokens
            if texto_media and texto_doc:
                prompt_final = prompt_base + f"\n[EXTRACCIÓN MULTIMEDIA DE LA PONENCIA]:\n{texto_media}\n\n[LITERATURA DE REFERENCIA]:\n{texto_doc}"
            elif texto_media:
                prompt_final = prompt_base + f"\n[EXTRACCIÓN MULTIMEDIA DE LA PONENCIA]:\n{texto_media}"
            elif texto_doc:
                prompt_final = prompt_base + f"\n[LITERATURA DE REFERENCIA]:\n{texto_doc}"
                
            response = model.generate_content(prompt_final)
            return response.text

    except Exception as e:
        return f"Error técnico en el motor LLM: {str(e)}"
