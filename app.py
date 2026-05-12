import streamlit as st
import sys
import os

# Inyección de ruta para resolver fallos de montaje en el servidor de Streamlit
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# Importación de los módulos lógicos (Pipeline)
from utils.doc_processor import process_document
from utils.asr_client import transcribe_audio
from utils.llm_client import process_with_llm

# 1. Configuración de la Interfaz Estricta
st.set_page_config(
    page_title="Procesador ASR y Análisis Semántico",
    page_icon="🩺",
    layout="wide"
)

st.title("Sistema de Transcripción y Estructuración Lógica")
st.markdown("Plataforma de síntesis de audio mediante inferencia acústica y contexto bibliográfico.")
st.markdown("---")

# 2. Ingesta de Datos (Columnas de UI)
col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Ingesta de Datos Acústicos")
    audio_file = st.file_uploader(
        "Carga la grabación (Clase magistral, ponencia, etc.) [.wav, .mp3, .m4a]", 
        type=["wav", "mp3", "m4a"]
    )
    
with col2:
    st.subheader("2. Contexto Bibliográfico (Opcional)")
    doc_file = st.file_uploader(
        "Carga el material de referencia para fijar terminología [.pdf, .pptx]", 
        type=["pdf", "pptx"]
    )

st.markdown("---")

# 3. Controlador Lógico (Orquestador)
if st.button("Ejecutar Pipeline de Procesamiento", type="primary"):
    
    if not audio_file and not doc_file:
        st.error("Error: Debes cargar al menos un vector de datos (Audio o Documento).")
    
    else:
        with st.spinner("Inicializando motores de procesamiento..."):
            
            # Variables temporales para el flujo
            texto_crudo = None
            contexto_doc = None
            
            # A. Procesamiento Documental
            if doc_file:
                with st.spinner("Extrayendo contexto bibliográfico (Ground Truth)..."):
                    contexto_doc = process_document(doc_file)
                    if contexto_doc and "Error" in contexto_doc:
                        st.error(contexto_doc)
                        st.stop() # Detiene la ejecución si hay un error crítico
            
            # B. Procesamiento Acústico
            if audio_file:
                with st.spinner("Ejecutando inferencia acústica (Whisper)..."):
                    texto_crudo = transcribe_audio(audio_file)
                    if isinstance(texto_crudo, str) and "Error" in texto_crudo:
                        st.error(texto_crudo)
                        st.stop()
            
            # C. Inferencia Semántica y Síntesis
            with st.spinner("Aplicando rigor técnico y generando síntesis (Gemini)..."):
                resultado_final = process_with_llm(
                    raw_transcript=texto_crudo, 
                    document_context=contexto_doc
                )
            
            # 4. Despliegue de Resultados
            st.success("Proceso completado con éxito.")
            
            st.markdown("### Resumen Estructurado")
            # st.write renderiza el formato Markdown que nos devuelve Gemini
            st.write(resultado_final)
            
            # Mostrar la transcripción cruda en un panel expansible
            if texto_crudo:
                with st.expander("Ver Transcripción Acústica Cruda (Sin corregir)"):
                    st.write(texto_crudo)
