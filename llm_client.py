import google.generativeai as genai
import streamlit as st
import time

def fraccionar_texto(texto, limite_caracteres=18000):
    """Corta un texto largo en fragmentos más pequeños respetando los saltos de línea."""
    fragmentos = []
    while len(texto) > 0:
        if len(texto) <= limite_caracteres:
            fragmentos.append(texto)
            break
        
        # Buscar un buen punto de corte (doble salto de línea o punto)
        punto_corte = texto.rfind('\n\n', 0, limite_caracteres)
        if punto_corte == -1: 
            punto_corte = texto.rfind('\n', 0, limite_caracteres)
        if punto_corte == -1: 
            punto_corte = limite_caracteres
            
        fragmentos.append(texto[:punto_corte])
        texto = texto[punto_corte:]
        
    return fragmentos

def process_with_llm(texto_media=None, texto_doc=None, instrucciones_usuario=""):
    """
    Motor semántico con Chunking Dinámico (Fraccionamiento en Lotes)
    para evitar el Error 429 (Cuota Excedida) en la capa gratuita de Gemini.
    Incluye el prompt médico High-Yield completo e intacto.
    """
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('models/gemini-2.5-flash')
    
    # PROMPT 100% INTACTO CON TODAS LAS REGLAS DE MINERÍA Y FORMATO
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
    - Scores / Clasificaciones (Detalla la escala, ej. Child-Pugh, d'Amico, MELD, FIB-4).
    - Dosis Farmacológicas / Manejo Quirúrgico.
    - Complicaciones.

    FUSIÓN Y MINERÍA DE DATOS (REGLA CRÍTICA PARA EVITAR VACÍOS):
    La Ponencia (Audio) y el Material Bibliográfico (PDF) tienen el MISMO nivel de jerarquía. 
    Si una fuente omite un dato clínico (ej. un score o una dosis), PERO está presente en la otra, es tu OBLIGACIÓN extraer ese dato e integrarlo en la tabla. 
    Solo debes colocar "N/E" si la información no existe en NINGUNA de las dos fuentes. Si hay contradicción directa entre ambas, prioriza la bibliografía.

    FORMATO INTERNO DE LAS CELDAS:
    - Usa listas con viñetas separadas por la etiqueta HTML <br> (ej. - Dato 1<br>- Dato 2).
    - Coloca en **negrita** los parámetros, valores de scores, signos patognomónicos y medicamentos de 1ra línea.
    """
    
    # INYECCIÓN DEL USUARIO
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
        texto_media_seguro = texto_media if texto_media else ""
        texto_doc_seguro = texto_doc if texto_doc else ""
        
        biblio_context = f"\n\n[GROUND TRUTH BIBLIOGRÁFICO]:\n{texto_doc_seguro}" if texto_doc_seguro else ""
        
        # BUCLE DE FRACCIONAMIENTO ANTI-ERROR 429
        if len(texto_media_seguro) > 20000:
            lotes = fraccionar_texto(texto_media_seguro, 18000)
            resultados_completos = []
            
            barra_progreso = st.progress(0)
            st.info(f"El archivo es muy grande. Dividido en {len(lotes)} fragmentos para evitar colapso de red...")
            
            for i, fragmento in enumerate(lotes):
                
                nota_continuacion = "" if i == 0 else "\n[NOTA: Este es un fragmento de continuación. Sigue generando cuadros con el formato |---|---| y OBEDECE ESTRICTAMENTE LA INSTRUCCIÓN DEL USUARIO si la hay. Empieza directamente con el título ##. No repitas información previa.]"
                
                prompt_lote = prompt_base + f"\n[PONENCIA ORAL (FRAGMENTO {i+1})]:\n{fragmento}" + biblio_context + nota_continuacion
                
                respuesta = model.generate_content(prompt_lote)
                resultados_completos.append(respuesta.text.strip())
                
                progreso_actual = (i + 1) / len(lotes)
                barra_progreso.progress(progreso_actual)
                
                if i < len(lotes) - 1:
                    time.sleep(15) 
            
            barra_progreso.empty() 
            return "\n\n".join(resultados_completos)
            
        else:
            # Ejecución estándar para textos cortos
            prompt_final = prompt_base + f"\n[PONENCIA ORAL]:\n{texto_media_seguro}" + biblio_context
            response = model.generate_content(prompt_final)
            return response.text.strip()

    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "Quota" in error_msg:
            return "⚠️ **Límite de cuota superado.** Por favor, espera 1 minuto sin presionar el botón y vuelve a intentarlo."
        return f"Error técnico en LLM: {error_msg}"
