import streamlit as st
import google.generativeai as genai
# Importación de las variables sistémicas
from prompts import PROMPT_INTEGRADO, PROMPT_AUDIO, PROMPT_DOCUMENTO

def process_with_llm(raw_transcript: str = None, document_context: str = None) -> str:
    """
    Motor de inferencia semántica y estructuración jerárquica.
    Evalúa la disponibilidad de datos y enruta la solicitud al prompt correspondiente.
    """
    try:
        # Configuración segura de credenciales
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        
        # Instanciación del modelo. 
        model = genai.GenerativeModel('gemini-1.5-pro-latest')
        
        # Configuración determinista de hiperparámetros
        generation_config = genai.GenerationConfig(
            temperature=0.1,  # Minimiza la probabilidad de alteraciones semánticas
            top_p=0.8
        )

        # 1. Lógica de Enrutamiento Condicional
        if raw_transcript and document_context:
            input_data = f"--- TRANSCRIPCIÓN ASR ---\n{raw_transcript}\n\n--- CONTEXTO BIBLIOGRÁFICO ---\n{document_context}"
            prompt_sistema = PROMPT_INTEGRADO
            
        elif raw_transcript and not document_context:
            input_data = f"--- TRANSCRIPCIÓN ASR ---\n{raw_transcript}"
            prompt_sistema = PROMPT_AUDIO
            
        elif document_context and not raw_transcript:
            input_data = f"--- CONTEXTO BIBLIOGRÁFICO ---\n{document_context}"
            prompt_sistema = PROMPT_DOCUMENTO
            
        else:
            return "Error de Inferencia: Vectores nulos. Se requiere al menos un flujo de datos."

        # 2. Ejecución de la Inferencia
        response = model.generate_content(
            contents=[
                {"role": "user", "parts": [prompt_sistema, input_data]}
            ],
            generation_config=generation_config
        )
        
        return response.text

    except KeyError:
        return "Error de Configuración: No se encontró GEMINI_API_KEY en st.secrets."
    except Exception as e:
        return f"Error crítico en el motor LLM: {str(e)}"
