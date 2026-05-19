import google.generativeai as genai
import streamlit as st
import time

def process_with_llm(texto_media=None, texto_doc=None):
    """
    Motor semántico High-Yield Avanzado: Validación cruzada, síntesis modular
    por patología para preparación de exámenes, sin marcas de IA ni metatexto,
    con control de alucinaciones (N/E) y cuadro resumen final.
    """
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    
    # Selección del motor multimodal
    model = genai.GenerativeModel('models/gemini-2.5-flash')
    
    # Prompt Directivo Estricto: Enfoque absoluto en el examen y limpieza visual total
    prompt_base = """Actúa como un tutor médico experto en preparación para exámenes de licenciamiento y residencia médica. Tu única tarea es redactar una guía de estudio de 'Alto Rendimiento' (High-Yield), estructurada de forma impersonal.

    REGLAS ESTRICTAS DE SALIDA:
    1. EXCLUSIVIDAD DE CONTENIDO: PROHIBIDO incluir introducciones, saludos, comentarios explicativos, notas de la IA, avisos de error o despedidas. El documento debe comenzar directamente con el encabezado de la primera patología detectada.
    2. CERO CITAS O REFERENCIAS: NO incluyas bajo ningún concepto anotaciones de origen como "(Diapositiva X)", "(Página Y)" o "[Nombre de archivo]".
    3. AUDITORÍA SILENCIOSA: Compara el audio con la bibliografía. Si el ponente se equivocó o la información está incompleta, prioriza los datos de la bibliografía e intégralos directamente de forma fluida como la verdad absoluta, sin mencionar el error del docente.
    4. ESTILO TELEGRÁFICO: Usa viñetas cortas, directas y densas en información. Elimina oraciones de transición. Extrae solo el "dato preguntable". Resalta en **negrita** palabras clave, triadas, o signos patognomónicos.

    ESTRUCTURA CLÍNICA MODULAR:
    Aplica la siguiente estructura de forma independiente POR CADA patología o subtema clínico diferenciado que identifiques en el dataset (repite este bloque completo para cada enfermedad):

    ## [Nombre de la Patología / Condición]
    - **Definición / Etiología:** Genes clave, factores de riesgo primarios.
    - **Fisiopatología:** Mecanismo molecular o celular central resumido.
    - **Clínica:** Signos y síntomas patognomónicos, criterios diagnósticos y hallazgos cardinales.
    - **Diagnóstico:** Evaluación inicial, screening o de elección vs. Gold Standard (Criterio de referencia).
    - **Tratamiento:** Esquema farmacológico o quirúrgico de primera línea y alternativas principales.

    PROTOCOLO ANTI-ALUCINACIÓN:
    Si un campo específico (como un gen, el gold standard o el tratamiento) no se menciona en absoluto ni en la ponencia ni en la bibliografía, escribe estrictamente "N/E" (No Especificado). Queda totalmente prohibido deducir, asumir o inventar datos fuera de las fuentes provistas.

    AYUDA MEMORIA FINAL:
    Al final de todo el reporte, genera únicamente una sección titulada "### 📋 Cuadro Resumen (Ayuda Memoria)". Debajo de ella, construye una tabla en Markdown con las columnas exactas:
    | Patología / Concepto | Clínica Clave | Dx Gold Standard | Tx de 1ra Línea |

    DATOS CLÍNICOS PARA SÍNTESIS EXCLUSIVA:
    """
    
    if not texto_media and not texto_doc:
        return "Error: Ausencia de matrices de datos para el análisis."

    try:
        # =====================================================================
        # ALGORITMO DE BIFURCACIÓN DE CARGA (Para evadir límites de cuota TPM)
        # =====================================================================
        if texto_media and len(texto_media) > 30000:
            
            mitad = len(texto_media) // 2
            punto_corte = texto_media.find('\n\n', mitad)
            if punto_corte == -1: punto_corte = texto_media.find('\n', mitad)
            if punto_corte == -1: punto_corte = mitad
                
            parte_1 = texto_media[:punto_corte]
            parte_2 = texto_media[punto_corte:]
            
            biblio_context = f"\n\n[LITERATURA DE REFERENCIA (GROUND TRUTH)]:\n{texto_doc}" if texto_doc else "\n\n[LITERATURA DE REFERENCIA]: No provista."
            
            # --- Ejecución del Lote 1 (Se suprime la tabla para que no aparezca a la mitad) ---
            prompt_1 = prompt_base.replace(
                "AYUDA MEMORIA FINAL:", 
                "AYUDA MEMORIA FINAL: (OMITIR TABLA EN ESTA FASE. Genera únicamente los bloques modulares de las patologías identificadas)."
            ) + f"\n[PARTE 1 - PONENCIA]:\n{parte_1}" + biblio_context
            response_1 = model.generate_content(prompt_1)
            
            # Enfriamiento estricto para purgar la cuota de la API
            time.sleep(35) 
            
            # --- Ejecución del Lote 2 (Aquí se prosigue y se inyecta la tabla consolidada al final) ---
            prompt_2 = prompt_base + f"\n[PARTE 2 - PONENCIA (Continuación directa, mantén la estructura clínica modular y el hilo semántico sin repetir la introducción)]:\n{parte_2}" + biblio_context
            response_2 = model.generate_content(prompt_2)
            
            # Concatenación directa libre de marcas de sistema, banners o texto de la IA
            return f"{response_1.text.strip()}\n\n{response_2.text.strip()}"
        
        # =====================================================================
        # EJECUCIÓN ESTÁNDAR (Archivos breves o procesamiento directo)
        # =====================================================================
        else:
            if texto_media and texto_doc:
                prompt_final = prompt_base + f"\n[PONENCIA ORAL]:\n{texto_media}\n\n[LITERATURA DE REFERENCIA (GROUND TRUTH)]:\n{texto_doc}"
            elif texto_media:
                prompt_final = prompt_base + f"\n[PONENCIA ORAL]:\n{texto_media}\n\n(Nota: No se proporcionó bibliografía de contraste)."
            elif texto_doc:
                prompt_final = prompt_base + f"\n\n[LITERATURA DE REFERENCIA]:\n{texto_doc}"
                
            response = model.generate_content(prompt_final)
            return response.text.strip()

    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "Quota exceeded" in error_msg:
            return "⚠️ **Límite de cuota superado.** El volumen de información excede la capa gratuita temporalmente. Por favor, reintente en unos momentos."
        return f"Error técnico en el motor LLM: {error_msg}"
