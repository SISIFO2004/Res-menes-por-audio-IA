import google.generativeai as genai
import streamlit as st
import time

def process_with_llm(texto_media=None, texto_doc=None):
    """
    Motor semántico 100% Tabular. Extrae y formatea toda la información 
    clínica exclusivamente en matrices de conocimiento (cuadros).
    """
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('models/gemini-2.5-flash')
    
    prompt_base = """Actúa como un tutor médico experto en preparación para exámenes de licenciamiento y residencia médica. Tu única tarea es destilar toda la información en matrices de conocimiento (tablas) de alto rendimiento.

    REGLAS ESTRICTAS DE SALIDA:
    1. EXCLUSIVIDAD TABULAR: ESTRICTAMENTE PROHIBIDO redactar párrafos sueltos, introducciones o viñetas fuera de las tablas. El 100% de la información clínica debe estar contenida dentro de celdas. Solo puedes usar texto fuera de las tablas para los Títulos (##).
    2. AUDITORÍA SILENCIOSA: Si el audio y la bibliografía se contradicen, plasma únicamente el dato de la bibliografía en la tabla como la verdad absoluta.
    3. FORMATO INTERNO: Usa listas con viñetas cortas (-) dentro de las celdas de la tabla para que la información sea fácil de leer. Resalta en **negrita** el "dato preguntable" (signos patognomónicos, gold standards).

    ESTRUCTURA MODULAR EXIGIDA:
    Organiza la información de la clase en las siguientes tres tablas (omite la tabla si no hay datos de esa categoría en las fuentes):

    ## 1. Base Clínica y Fisiopatología
    | Patología / Concepto | Definición Clave | Etiología y Factores de Riesgo | Fisiopatología (Mecanismo Core) |

    ## 2. Herramientas Diagnósticas y Scores
    | Score / Herramienta | Parámetros Evaluados | Puntos de Corte / Criterios | Interpretación y Acción Clínica |

    ## 3. Complicaciones y Manejo Terapéutico
    | Complicación / Variante | Clínica y Criterios Dx | Profilaxis (Primaria/Secundaria) | Tratamiento Agudo / 1ra Línea |

    PROTOCOLO ANTI-ALUCINACIÓN:
    Si no hay datos para una celda específica, escribe "N/E". Prohibido inventar datos.

    DATOS PARA SÍNTESIS TABULAR:
    """
    
    if not texto_media and not texto_doc:
        return "Error: Ausencia de matrices de datos."

    try:
        if texto_media and len(texto_media) > 30000:
            mitad = len(texto_media) // 2
            punto_corte = texto_media.find('\n\n', mitad)
            if punto_corte == -1: punto_corte = texto_media.find('\n', mitad)
            if punto_corte == -1: punto_corte = mitad
                
            overlap_size = 800
            inicio_parte_2 = max(0, punto_corte - overlap_size)
            parte_1 = texto_media[:punto_corte]
            parte_2 = texto_media[inicio_parte_2:]
            
            biblio_context = f"\n\n[GROUND TRUTH]:\n{texto_doc}" if texto_doc else "\n\n[GROUND TRUTH]: No provista."
            
            prompt_1 = prompt_base + f"\n[PARTE 1 - PONENCIA]:\n{parte_1}" + biblio_context
            response_1 = model.generate_content(prompt_1)
            time.sleep(35) 
            
            prompt_2 = prompt_base + f"\n[PARTE 2 - PONENCIA (INCLUYE OVERLAP)]:\n[Nota para IA: Continúa rellenando el esquema tabular con la información restante de esta segunda parte. No repitas patologías de la parte 1].\n\n{parte_2}" + biblio_context
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
        if "429" in str(e) or "Quota" in str(e):
            return "⚠️ **Límite de cuota superado.** Por favor reintente luego."
        return f"Error LLM: {str(e)}"
