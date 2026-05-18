import google.generativeai as genai
import streamlit as st
import time

def process_with_llm(texto_media=None, texto_doc=None):
    """
    Motor semántico High-Yield: Validación cruzada, síntesis ultra-concisa
    para preparación de exámenes y cuadro resumen final.
    """
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    
    # Motor confirmado
    model = genai.GenerativeModel('models/gemini-2.5-flash')
    
    # Prompt Directivo Estricto: Estilo High-Yield para Exámenes Médicos
    prompt_base = """Actúa como un tutor médico experto en preparación para exámenes de licenciamiento y residencia médica. Tu objetivo es destilar la información proporcionada en una guía de estudio de 'Alto Rendimiento' (High-Yield), ultra-concisa y estructurada. ESTRICTAMENTE PROHIBIDO hacer transcripciones largas o resúmenes narrativos.

    INSTRUCCIONES DE SÍNTESIS (MODO EXAMEN):
    1. ESTILO TELEGRÁFICO: Usa viñetas cortas y directas. Elimina texto de relleno, anécdotas del ponente y explicaciones redundantes. Extrae solo el "dato preguntable". Resalta en **negrita** palabras clave, triadas, o signos patognomónicos.
    2. ESTRUCTURA CLÍNICA: Ordena la información de forma estandarizada: 
       - Definición / Etiología (Genes clave, factores de riesgo).
       - Fisiopatología (Solo el mecanismo core).
       - Clínica (Signos y síntomas principales).
       - Diagnóstico (Test inicial vs. Gold Standard).
       - Tratamiento (1ra línea y alternativas).
    3. AUDITORÍA CRUZADA: Compara el audio con la bibliografía. Si el ponente se equivocó, prioriza la bibliografía e indícalo brevemente: "[Corrección según doc: ...]". Rellena vacíos del audio con los PDFs/PPTXs.
    4. TABLA AYUDA MEMORIA (HIGH-YIELD): Al final del reporte, crea obligatoriamente la sección "### 📋 Cuadro Resumen (Ayuda Memoria)". Inserta una tabla Markdown con las columnas: [Patología/Concepto] | [Clínica Clave] | [Dx Gold Standard] | [Tx de 1ra Línea].

    DATOS CLÍNICOS PARA SÍNTESIS:
    """
    
    if not texto_media and not texto_doc:
        return "Error: Ausencia de matrices de datos para el análisis."

    try:
        # =====================================================================
        # ALGORITMO DE BIFURCACIÓN (Para archivos extensos)
        # =====================================================================
        if texto_media and len(texto_media) > 30000:
            
            mitad = len(texto_media) // 2
            punto_corte = texto_media.find('\n\n', mitad)
            if punto_corte == -1: punto_corte = texto_media.find('\n', mitad)
            if punto_corte == -1: punto_corte = mitad
                
            parte_1 = texto_media[:punto_corte]
            parte_2 = texto_media[punto_corte:]
            
            biblio_context = f"\n\n[LITERATURA DE REFERENCIA (GROUND TRUTH)]:\n{texto_doc}" if texto_doc else "\n\n[LITERATURA DE REFERENCIA]: No provista. Basa el análisis solo en el multimedia."
            
            # --- Ejecución del Lote 1 ---
            # Suprimimos la orden de la tabla para que no la genere a la mitad del documento
            prompt_1 = prompt_base.replace("4. TABLA AYUDA MEMORIA (HIGH-YIELD): Al final del reporte, crea obligatoriamente la sección", "4. (OMITIR TABLA EN ESTA FASE)") + f"\n[PARTE 1 - PONENCIA ORAL]:\n{parte_1}" + biblio_context
            response_1 = model.generate_content(prompt_1)
            
            time.sleep(35) 
            
            # --- Ejecución del Lote 2 ---
            prompt_2 = prompt_base + f"\n[PARTE 2 - PONENCIA ORAL]:\n{parte_2}" + biblio_context
            response_2 = model.generate_content(prompt_2)
            
            return f"### 📊 FASE 1: SÍNTESIS HIGH-YIELD\n\n{response_1.text}\n\n---\n\n### 📊 FASE 2: SÍNTESIS HIGH-YIELD\n\n{response_2.text}"
        
        # =====================================================================
        # EJECUCIÓN ESTÁNDAR 
        # =====================================================================
        else:
            if texto_media and texto_doc:
                prompt_final = prompt_base + f"\n[PONENCIA ORAL]:\n{texto_media}\n\n[LITERATURA DE REFERENCIA (GROUND TRUTH)]:\n{texto_doc}"
            elif texto_media:
                prompt_final = prompt_base + f"\n[PONENCIA ORAL]:\n{texto_media}\n\n(Nota: No se proporcionó bibliografía de contraste. Analiza solo la ponencia)."
            elif texto_doc:
                prompt_final = prompt_base + f"\n(Nota: No hay ponencia oral. Resume y estructura esta literatura médica en formato High-Yield):\n\n[LITERATURA DE REFERENCIA]:\n{texto_doc}"
                
            response = model.generate_content(prompt_final)
            return response.text

    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "Quota exceeded" in error_msg:
            return "⚠️ **Límite de cuota de Google superado.** El volumen de información excede la capa gratuita (Límite diario o por minuto). Te sugiero usar archivos más cortos o reintentar en 24 horas."
        return f"Error técnico en el motor LLM: {error_msg}"
