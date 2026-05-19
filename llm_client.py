import google.generativeai as genai
import streamlit as st
import time

def process_with_llm(texto_media=None, texto_doc=None):
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('models/gemini-2.5-flash')
    
    prompt_base = """Actúa como un tutor médico experto en preparación para exámenes de licenciamiento y residencia médica. Tu única tarea es redactar una guía de estudio de 'Alto Rendimiento' (High-Yield), estructurada de forma impersonal.

    REGLAS ESTRICTAS DE SALIDA:
    1. EXCLUSIVIDAD DE CONTENIDO: PROHIBIDO incluir introducciones, saludos o notas de IA. Empieza directo con las patologías.
    2. CERO CITAS O REFERENCIAS: NO incluyas bajo ningún concepto anotaciones de origen (ej. "Diapositiva X").
    3. AUDITORÍA SILENCIOSA: Prioriza y aplica los datos de la bibliografía como la verdad absoluta si hay contradicciones.
    4. ESTILO TELEGRÁFICO: Viñetas cortas. Extrae solo el "dato preguntable". Resalta en **negrita** palabras clave.

    ESTRUCTURA CLÍNICA MODULAR (Repetir por cada patología):
    ## [Nombre de la Patología]
    - **Definición / Etiología:** Genes, factores de riesgo.
    - **Fisiopatología:** Mecanismo core.
    - **Clínica:** Signos patognomónicos, hallazgos cardinales.
    - **Diagnóstico:** Inicial vs. Gold Standard.
    - **Tratamiento:** Primera línea y alternativas.

    PROTOCOLO ANTI-ALUCINACIÓN:
    Si un dato no existe en las fuentes, escribe estrictamente "N/E". Prohibido inventar datos.

    AYUDA MEMORIA FINAL:
    Al final de todo el reporte, genera únicamente una sección titulada "### 📋 Cuadro Resumen (Ayuda Memoria)". Debajo, construye una tabla Markdown con las columnas exactas:
    | Patología / Concepto | Clínica Clave | Dx Gold Standard | Tx de 1ra Línea |

    DATOS CLÍNICOS PARA SÍNTESIS EXCLUSIVA:
    """
    
    if not texto_media and not texto_doc:
        return "Error: Ausencia de matrices de datos."

    try:
        # =====================================================================
        # BIFURCACIÓN CON SOLAPAMIENTO (OVERLAP)
        # =====================================================================
        if texto_media and len(texto_media) > 30000:
            
            mitad = len(texto_media) // 2
            punto_corte = texto_media.find('\n\n', mitad)
            if punto_corte == -1: punto_corte = texto_media.find('\n', mitad)
            if punto_corte == -1: punto_corte = mitad
                
            parte_1 = texto_media[:punto_corte]
            
            # Algoritmo Overlap: Retrocedemos 800 caracteres para no perder contexto
            overlap_size = 800
            inicio_parte_2 = max(0, punto_corte - overlap_size)
            parte_2 = texto_media[inicio_parte_2:]
            
            biblio_context = f"\n\n[GROUND TRUTH]:\n{texto_doc}" if texto_doc else "\n\n[GROUND TRUTH]: No provista."
            
            # --- Fase 1 ---
            prompt_1 = prompt_base.replace(
                "AYUDA MEMORIA FINAL:", 
                "AYUDA MEMORIA FINAL: (OMITIR TABLA EN ESTA FASE. Genera solo los bloques de patologías)."
            ) + f"\n[PARTE 1 - PONENCIA]:\n{parte_1}" + biblio_context
            response_1 = model.generate_content(prompt_1)
            
            time.sleep(35) 
            
            # --- Fase 2 (Con advertencia de solapamiento para la IA) ---
            prompt_2 = prompt_base + f"\n[PARTE 2 - PONENCIA (INCLUYE OVERLAP DE CONTEXTO)]:\n[Nota para IA: Los primeros párrafos son un solapamiento de la Fase 1 para mantener el hilo. No repitas patologías que ya extrajiste, continúa desde donde te quedaste].\n\n{parte_2}" + biblio_context
            response_2 = model.generate_content(prompt_2)
            
            return f"{response_1.text.strip()}\n\n{response_2.text.strip()}"
            
        else:
            if texto_media and texto_doc:
                prompt_final = prompt_base + f"\n[PONENCIA]:\n{texto_media}\n\n[GROUND TRUTH]:\n{texto_doc}"
            elif texto_media:
                prompt_final = prompt_base + f"\n[PONENCIA]:\n{texto_media}\n\n(No hay bibliografía)."
            elif texto_doc:
                prompt_final = prompt_base + f"\n\n[BIBLIOGRAFÍA]:\n{texto_doc}"
                
            response = model.generate_content(prompt_final)
            return response.text.strip()

    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "Quota" in error_msg:
            return "⚠️ **Límite de cuota superado.** Por favor reintente luego."
        return f"Error LLM: {error_msg}"
