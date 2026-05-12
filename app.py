import streamlit as st

# Importación directa de lógica (Estructura Plana)
from doc_processor import process_document
from asr_client import transcribe_audio
from llm_client import process_with_llm

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
coll, col2 = st.columns(2)

with coll:
    audio_file = st.file_uploader(
        "Carga la grabación (Clase magistral, ponencia, etc.) [.wav, .mp3, .m4a]",
        type=["wav", "mp3", "m4a"]
    )

with col2:
    doc_file = st.file_uploader(
        "Carga bibliografía de referencia (Opcional) [.pdf, .pptx]",
        type=["pdf", "pptx"]
    )

# 3. Pipeline de Ejecución
if st.button("Ejecutar Pipeline"):
    if not audio_file and not doc_file:
        st.error("Error: Se requiere al menos una fuente de entrada (audio o documento).")
    else:
        with st.spinner("Procesando información..."):
            # Procesamiento de Documento
            contexto_doc = None
            if doc_file:
                contexto_doc = process_document(doc_file)
            
            # Procesamiento de Audio
            transcripcion = None
            if audio_file:
                transcripcion = transcribe_audio(audio_file)
            
            # Generación de Resumen Estructurado (Inferencia Semántica)
            resultado = process_with_llm(transcripcion, contexto_doc)
            
            st.markdown("### Resultado del Análisis Científico")
            st.write(resultado)
