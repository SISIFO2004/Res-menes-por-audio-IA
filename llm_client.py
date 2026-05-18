import google.generativeai as genai
import streamlit as st
import time

def process_with_llm(texto_media=None, texto_doc=None):
    """
    Motor semántico avanzado con capacidad de auditoría clínica cruzada
    y algoritmo de bifurcación de carga para evadir límites de cuota (TPM).
    """
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    
    # Inyección del modelo soportado por la credencial actual
    model = genai.GenerativeModel('models/gemini-2.5-flash')
    
    # Prompt Directivo Estricto: Auditoría y Ground Truth
    prompt_base = """Actúa como un auditor médico de alto nivel académico. Tu directiva principal es realizar una validación cruzada (cross-reference) entre la transcripción de la ponencia oral y la literatura bibliográfica proporcionada.

    INSTRUCCIONES DE AUDITORÍA:
    1. CONTRASTE: Compara lo dicho en la ponencia oral con los documentos de referencia. 
    2. CORRECCIÓN: Si detectas que el ponente mencionó un dato incorrecto (ej. dosis, gen, vía metabólica) o incompleto que se contradice con la bibliografía, prioriza la bibliografía. Señala la corrección en el resumen indicando la fuente (ej. "Corrección según Diapositiva 4...").
    3. SÍNTESIS RETROALIMENTADA: Rellena los vacíos de información de la ponencia utilizando los datos complementarios de los PDFs/PPTXs.
    4. FORMATO: Genera el reporte definitivo en formato Markdown con viñetas claras, estructurado lógicamente por patologías, diagnóstico o tratamiento. NO saludes, no pidas más datos ni utilices analogías.

    DATOS CLÍNICOS PARA AUDITORÍA Y ANÁLISIS:
    """
    
    if not texto_media and not texto_doc:
        return "Error: Ausencia de matrices de datos para el análisis."

    try:
        # =====================================================================
        # ALGORITMO DE BIFURCACIÓN (Para archivos de audio/video extensos)
        # Umbral configurado a 30,000 caracteres (aprox. 30-40 minutos de clase)
        # =====================================================================
        if texto_media and len(texto_media) > 30000:
            
            # Búsqueda de un punto de corte seguro para no romper oraciones
            mitad = len(texto_media) // 2
            punto_corte = texto_media.find('\n\n', mitad)
            if punto_corte == -1: 
                punto_corte = texto_media.find('\n', mitad)
            if punto_corte == -1: 
                punto_corte = mitad
                
            parte_1 = texto_media[:punto_corte]
            parte_2 = texto_media[punto_corte:]
            
            # Preparación de la bibliografía (Ground Truth) para inyectar en ambas fases
            biblio_context = f"\n\n[LITERATURA DE REFERENCIA (GROUND TRUTH)]:\n{texto_doc}" if texto_doc else "\n\n[LITERATURA DE REFERENCIA]: No provista. Basa el análisis solo en el multimedia."
            
            # --- Ejecución del Lote 1 ---
            prompt_1 = prompt_base + f"\n[PARTE 1 - PONENCIA ORAL]:\n{parte_1}" + biblio_context
            response_1 = model.generate_content(prompt_1)
            
            # Pausa estricta de 35 segundos para purgar la cuota TPM de la API
            time.sleep(35) 
            
            # --- Ejecución del Lote 2 ---
            prompt_2 = prompt_base + f"\n[PARTE 2 - PONENCIA ORAL]:\n{parte_2}" + biblio_context
            response_2 = model.generate_content(prompt_2)
            
            # Concatenación de resultados estructurados
            return f"### 📊 FASE 1: AUDITORÍA Y SÍNTESIS\n\n{response_1.text}\n\n---\n\n### 📊 FASE 2: AUDITORÍA Y SÍNTESIS\n\n{response_2.text}"
        
        # =====================================================================
        # EJECUCIÓN ESTÁNDAR (Para archivos cortos o solo documentos)
        # =====================================================================
        else:
            if texto_media and texto_doc:
                prompt_final = prompt_base + f"\n[PONENCIA ORAL]:\n{texto_media}\n\n[LITERATURA DE REFERENCIA (GROUND TRUTH)]:\n{texto_doc}"
            elif texto_media:
                prompt_final = prompt_base + f"\n[PONENCIA ORAL]:\n{texto_media}\n\n(Nota: No se proporcionó bibliografía de contraste. Analiza solo la ponencia)."
            elif texto_doc:
                prompt_final = prompt_base + f"\n(Nota: No hay ponencia oral. Resume y estructura esta literatura médica de forma rigurosa):\n\n[LITERATURA DE REFERENCIA]:\n{texto_doc}"
                
            response = model.generate_content(prompt_final)
            return response.text

    except Exception as e:
        error_msg = str(e)
        # Captura específica de errores de límite de cuota (RPD o TPM extremos)
        if "429" in error_msg or "Quota exceeded" in error_msg:
            return "⚠️ **Límite de cuota de Google superado.** El volumen de información excede la capa gratuita (Límite diario o por minuto). Te sugiero usar archivos más cortos o reintentar en 24 horas."
        return f"Error técnico en el motor LLM: {error_msg}"
