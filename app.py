import streamlit as st
from doc_processor import process_document
from asr_client import transcribe_media
from llm_client import process_with_llm

st.set_page_config(page_title="Análisis Semántico Médico", page_icon="🩺", layout="wide")

st.title("Sistema de Resúmenes Médicos (Motor Gemini 2.5)")
st.markdown("Plataforma técnica para la síntesis de clases magistrales y bibliografía.")

col1, col2 = st.columns(2)
with col1:
    # Soporte añadido para .mp4
    media_file = st.file_uploader("Multimedia de la ponencia [.wav, .mp3, .m4a, .mp4]", type=["wav", "mp3", "m4a", "mp4"])
with col2:
    doc_file = st.file_uploader("Documento de referencia [.pdf, .pptx]", type=["pdf", "pptx"])

if st.button("Ejecutar Pipeline de Análisis", type="primary"):
    if not media_file and not doc_file:
        st.error("Protocolo interrumpido: Se requiere al menos una fuente de datos.")
    else:
        with st.spinner("Realizando inferencia semántica y visual..."):
            texto_doc = process_document(doc_file) if doc_file else None
            texto_media = transcribe_media(media_file) if media_file else None
            
            resultado = process_with_llm(texto_media, texto_doc)
            
            st.success("Análisis completado exitosamente.")
            st.markdown("---")
            st.markdown(resultado)
            
            if texto_media:
                with st.expander("Ver Log de Extracción Multimedia"):
                    st.write(texto_media)
