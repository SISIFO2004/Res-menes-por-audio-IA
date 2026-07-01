import google.generativeai as genai
import streamlit as st
import time

def process_with_llm(texto_media=None, texto_doc=None, instrucciones_usuario=""):
    """
    Motor semántico (Estilo Fichas de Estudio Clínico): 
    Arquitectura de Fusión Total con soporte para inyección de directivas dinámicas del usuario.
    """
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('models/gemini-2.5-flash')
    
    prompt_base = """Actúa como un arquitecto de datos médicos elaborando cuadros de estudio avanzados para preparación médica. Tu objetivo es la máxima densidad de datos con el mínimo de palabras.

    REGLAS ESTRICTAS DE REDACCIÓN (CERO CONVERSACIÓN):
    1. ARRANQUE DIRECTO: ESTRICTAMENTE PROHIBIDO incluir saludos, introducciones, confirmaciones, comentarios de IA o despedidas. Inicia el documento DIRECTAMENTE con el encabezado '##' de la primera patología.
    2. ESTILO TELEGRÁFICO: CERO narrativa. CERO párrafos explicativos. Usa frases cortadas.
    3. SECUENCIAS LÓGICAS: Para la fisiopatología, NO redactes. Usa secuencias con flechas (Ej. Daño celular -> Activación miofibroblastos -> Fibrosis).
    4. DENSIDAD CUANTITATIVA: Extrae y resalta dosis exactas (ej. 100mg/24h), puntos de corte (ej. PMN ≥ 250), porcentajes epidemiológicos y tiempos.
    5. ABREVIATURAS MÉDICAS: Emplea acrónimos estándar.
    
    ESTRUCTURA EXCLUSIVA POR ENFERMEDAD:
    Por cada patología o condición, crea un título con '##' seguido EXACTAMENTE por esta cabecera Markdown estricta:
    | Eje Clínico | Contenido |
    |---|---|
    
    El 100% de la información DEBE estar dentro de las filas siguientes. PROHIBIDO usar múltiples barras verticales '||' o alterar los guiones de la cabecera. NO agregues texto fuera de los cuadros.

    EJES CLÍNICOS DINÁMICOS (OBLIGATORIOS):
    Debes incluir ejes básicos, pero es OBLIGATORIO crear nuevas filas si detectas:
    - Epidemiología / Factores de Riesgo.
    - Criterios Diagnósticos exactos.
    - Scores / Clasificaciones.
    - Dosis Farmacológicas / Manejo Quirúrgico.
    - Complicaciones.

    FUSIÓN Y MINERÍA DE DATOS:
    La Ponencia (Audio) y el Material Bibliográfico (PDF) tienen el MISMO nivel de jerarquía. Rellena los vacíos de una fuente usando la otra.
    """
    
    # =====================================================================
    # INYECCIÓN DINÁMICA DE LA ORDEN DEL USUARIO (OVERRIDE)
    # =====================================================================
    if instrucciones_usuario and instrucciones_usuario.strip() != "":
        prompt_base += f"""
    ======================================================================
    🚨 INSTRUCCIÓN ESPECIAL DEL USUARIO (PRIORIDAD MÁXIMA) 🚨
    El usuario ha dado la siguiente directiva específica para este análisis:
    "{instrucciones_usuario}"
    
    DEBES OBEDECER ESTA INSTRUCCIÓN POR ENCIMA DE CUALQUIER OTRA REGLA.
    Si el usuario te pide omitir ciertos ejes (ej. no incluir fisiopatología), omítelos. Si te pide ser extremadamente breve, recorta la información. Si te pide enfocarte solo en un aspecto (ej. solo tratamiento), ajusta el contenido de las tablas SOLO a eso.
    ======================================================================
    """
    
    prompt_base += "\nDATOS PARA SÍNTESIS TABULAR:\n"
    
    if not texto_media and not texto_doc:
        return "Error: Ausencia de matrices de datos para el análisis."

    try:
        # =====================================================================
        # BIFURCACIÓN DE CARGA (Con algoritmo Overlap de 800 caracteres)
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
            
            prompt_1 = prompt_base + f"\n[PARTE 1 - PONENCIA]:\n{parte_1}" + biblio_context
            response_1 = model.generate_content(prompt_1)
            
            time.sleep(35) 
            
            prompt_2 = prompt_base + f"\n[PARTE 2 - PONENCIA (INCLUYE OVERLAP)]:\n[Nota algorítmica: Continúa el formato y OBEDECE ESTRICTAMENTE LA INSTRUCCIÓN DEL USUARIO si la hay. Empieza directamente con el título ##].\n\n{parte_2}" + biblio_context
            response_2 = model.generate_content(prompt_2)
            
            return f"{response_1.text.strip()}\n\n{response_2.text.strip()}"
            
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
