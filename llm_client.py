import google.generativeai as genai
import streamlit as st
import time

def process_with_llm(texto_media=None, texto_doc=None):
    """
    Motor semántico High-Yield (Estilo Sábana Clínica): 
    Fuerza al LLM a comportarse como un arquitecto de datos, priorizando 
    estilo telegráfico, abreviaturas, scores y secuencias lógicas.
    """
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('models/gemini-2.5-flash')
    
    prompt_base = """Actúa como un arquitecto de datos médicos elaborando "sábanas de estudio" (fichas High-Yield) para academias de preparación de residencia médica (tipo CTO, Villamedic). Tu objetivo es la máxima densidad de datos con el mínimo de palabras.

    REGLAS ESTRICTAS DE REDACCIÓN (ESTILO ACADEMIA):
    1. ESTILO TELEGRÁFICO: CERO narrativa. CERO párrafos explicativos. Usa frases cortadas.
    2. SECUENCIAS LÓGICAS: Para la fisiopatología, NO redactes. Usa secuencias con flechas (Ej. Daño celular -> Activación miofibroblastos -> Fibrosis -> Hipertensión Portal).
    3. DENSIDAD CUANTITATIVA: Extrae y resalta agresivamente dosis exactas (ej. 100mg/24h), puntos de corte (ej. PMN ≥ 250), porcentajes epidemiológicos y tiempos.
    4. ABREVIATURAS MÉDICAS: Emplea acrónimos estándar (HTP, PBE, IBP, TIPS, etc.) para ahorrar espacio.
    
    ESTRUCTURA EXCLUSIVA POR ENFERMEDAD:
    Por cada patología, complicación o condición, crea un título con '##' seguido de una tabla de dos columnas: | Eje Clínico | Contenido High-Yield |. 
    El 100% de la información clínica DEBE estar dentro de esta tabla.

    EJES CLÍNICOS DINÁMICOS (OBLIGATORIOS):
    Debes incluir ejes básicos, pero es OBLIGATORIO crear nuevas filas si detectas:
    - Epidemiología / Factores de Riesgo.
    - Criterios Diagnósticos exactos.
    - Scores / Clasificaciones (Detalla la escala, ej. Child-Pugh, d'Amico, MELD, FIB-4).
    - Dosis Farmacológicas / Manejo Quirúrgico.
    - Complicaciones.

    FORMATO INTERNO DE LAS CELDAS:
    - Usa listas con viñetas separadas por la etiqueta HTML <br> (ej. - Dato 1<br>- Dato 2).
    - Coloca en **negrita** los parámetros, valores de scores, signos patognomónicos y medicamentos de 1ra línea.

    AUDITORÍA SILENCIOSA:
    Ante cualquier contradicción entre la ponencia y la bibliografía, asume los datos de la bibliografía como la verdad absoluta y plásmalos sin mencionar el error.

    DATOS PARA SÍNTESIS TABULAR DE ALTO RENDIMIENTO:
    """
    
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
            
            # --- Fase 1 ---
            prompt_1 = prompt_base + f"\n[PARTE 1 - PONENCIA]:\n{parte_1}" + biblio_context
            response_1 = model.generate_content(prompt_1)
            
            time.sleep(35) # Respetando límites de cuota TPM
            
            # --- Fase 2 ---
            prompt_2 = prompt_base + f"\n[PARTE 2 - PONENCIA (INCLUYE OVERLAP)]:\n[Nota algorítmica: Continúa el formato de tablas independientes. Exprime las dosis, scores y usa flechas lógicas. No repitas tablas ya creadas en la parte 1].\n\n{parte_2}" + biblio_context
            response_2 = model.generate_content(prompt_2)
            
            return f"{response_1.text.strip()}\n\n{response_2.text.strip()}"
            
        # =====================================================================
        # EJECUCIÓN ESTÁNDAR 
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
