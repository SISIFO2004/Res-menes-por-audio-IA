import google.generativeai as genai
import streamlit as st
import time

def process_with_llm(texto_media=None, texto_doc=None):
    """
    Motor semántico de alta fidelidad: Genera tablas verticales independientes
    por patología, con Ejes Clínicos Dinámicos para evitar pérdida de datos (Scores, Clasificaciones).
    """
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('models/gemini-2.5-flash')
    
    prompt_base = """Actúa como un tutor médico experto en preparación para exámenes de licenciamiento y residencia médica. Tu única tarea es destilar toda la información en tablas independientes por cada patología, síndrome o condición identificada.

    REGLAS ESTRICTAS DE SALIDA:
    1. ESTRUCTURA EXCLUSIVA POR ENFERMEDAD: Por cada patología, debes crear un título con '##' seguido de inmediato por una tabla de exactamente dos columnas: | Eje Clínico | Contenido de Alto Rendimiento (High-Yield) |.
    2. EXCLUSIVIDAD TABULAR: El 100% de los datos clínicos debe estar dentro de la tabla. No redactes párrafos introductorios ni texto fuera de las tablas.
    3. EJES CLÍNICOS DINÁMICOS (CERO PÉRDIDA DE DATOS): Debes incluir los ejes básicos (Definición/Etiología, Fisiopatología, Clínica, Diagnóstico, Tratamiento). SIN EMBARGO, es OBLIGATORIO crear filas adicionales (nuevos Ejes Clínicos) si el texto menciona:
       - Epidemiología (porcentajes, prevalencia).
       - Clasificaciones / Scores (ej. Child-Pugh, Forrest, d'Amico, Praga).
       - Complicaciones.
       - Pronóstico o Prevención.
       Ningún dato, porcentaje o score debe quedar fuera del resumen.
    4. FORMATO INTERNO: Dentro de la celda de contenido, usa listas cortas con viñetas (-) separadas por etiquetas <br> si hay múltiples puntos. Coloca en **negrita** los datos de alta rentabilidad (gold standards, signos patognomónicos, parámetros de scores, dosis).
    5. AUDITORÍA SILENCIOSA: Si el audio contradice a la bibliografía, plasma únicamente el dato de la bibliografía como verdad absoluta.

    FORMATO OBLIGATORIO (Ejemplo expansible):
    ## [Nombre de la Patología / Condición]
    | Eje Clínico | Contenido de Alto Rendimiento (High-Yield) |
    | :--- | :--- |
    | **Definición / Etiología** | - [Datos estructurados aquí] |
    | **Fisiopatología** | - [Mecanismo core aquí] |
    | **Clínica** | - [Signos cardinales] |
    | **Clasificaciones / Scores** | - [Añadir esta fila si aplica, detallando criterios] |
    | **Diagnóstico** | - [Test inicial vs. Gold Standard] |
    | **Tratamiento** | - [Primera línea, dosis] |
    | **Complicaciones** | - [Añadir esta fila si aplica] |

    PROTOCOLO ANTI-ALUCINACIÓN:
    Si un eje básico no se menciona en absoluto en ninguna de las fuentes, escribe estrictamente "N/E". Prohibido inventar información médica.

    DATOS PARA SÍNTESIS TABULAR EXHAUSTIVA:
    """
    
    if not texto_media and not texto_doc:
        return "Error: Ausencia de matrices de datos para el análisis."

    try:
        # =====================================================================
        # BIFURCACIÓN DE CARGA (Para clases largas, con algoritmo Overlap)
        # =====================================================================
        if texto_media and len(texto_media) > 30000:
            
            mitad = len(texto_media) // 2
            punto_corte = texto_media.find('\n\n', mitad)
            if punto_corte == -1: punto_corte = texto_media.find('\n', mitad)
            if punto_corte == -1: punto_corte = mitad
                
            overlap_size = 800
            inicio_parte_2 = max(0, punto_corte - overlap_size)
            parte_1 = texto_media[:punto_corte]
            parte_2 = texto_media[inicio_parte_2:]
            
            biblio_context = f"\n\n[GROUND TRUTH BIBLIOGRÁFICO]:\n{texto_doc}" if texto_doc else "\n\n[GROUND TRUTH]: No provista."
            
            # --- Fase 1 ---
            prompt_1 = prompt_base + f"\n[PARTE 1 - PONENCIA ORAL]:\n{parte_1}" + biblio_context
            response_1 = model.generate_content(prompt_1)
            
            time.sleep(35) # Enfriamiento de cuota API
            
            # --- Fase 2 ---
            prompt_2 = prompt_base + f"\n[PARTE 2 - PONENCIA ORAL (INCLUYE OVERLAP)]:\n[Nota algorítmica para IA: Continúa el esquema de tablas independientes para las patologías restantes. Asegúrate de incluir todos los scores y clasificaciones. No repitas tablas ya creadas en la parte 1].\n\n{parte_2}" + biblio_context
            response_2 = model.generate_content(prompt_2)
            
            return f"{response_1.text.strip()}\n\n{response_2.text.strip()}"
            
        # =====================================================================
        # EJECUCIÓN ESTÁNDAR (Archivos cortos o solo documentos)
        # =====================================================================
        else:
            if texto_media and texto_doc:
                prompt_final = prompt_base + f"\n[PONENCIA ORAL]:\n{texto_media}\n\n[GROUND TRUTH BIBLIOGRÁFICO]:\n{texto_doc}"
            elif texto_media:
                prompt_final = prompt_base + f"\n[PONENCIA ORAL]:\n{texto_media}\n\n(No hay bibliografía de contraste)."
            elif texto_doc:
                prompt_final = prompt_base + f"\n\n[MATERIAL BIBLIOGRÁFICO]:\n{texto_doc}"
                
            response = model.generate_content(prompt_final)
            return response.text.strip()

    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "Quota" in error_msg:
            return "⚠️ **Límite de cuota superado.** El volumen excede el límite temporal de la API. Por favor, reintente en unos minutos."
        return f"Error técnico en LLM: {error_msg}"
