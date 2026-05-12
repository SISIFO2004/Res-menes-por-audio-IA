import streamlit as st
from doc_processor import process_document
from asr_client import transcribe_audio
from llm_client import process_with_llm

st.set_page_config(page_title="Análisis Semántico Médico", page_icon="🩺", layout="wide")

st.title("Sistema de Resúmenes Médicos (Motor Gemini 2.5)")
st.markdown("Plataforma técnica para la síntesis de clases magistrales y bibliografía.")

col1, col2 = st.columns(2)
with col1:
    audio_file = st.file_uploader("Audio de la ponencia [.wav, .mp3, .m4a]", type=["wav", "mp3", "m4a"])
with col2:
    doc_file = st.file_uploader("Documento de referencia [.pdf, .pptx]", type=["pdf", "pptx"])

if st.button("Ejecutar Pipeline de Análisis", type="primary"):
    if not audio_file and not doc_file:
        st.error("Protocolo interrumpido: Se requiere al menos una fuente de datos.")
    else:
        with st.spinner("Realizando inferencia semántica..."):
            texto_doc = process_document(doc_file) if doc_file else None
            texto_audio = transcribe_audio(audio_file) if audio_file else None
            
            resultado = process_with_llm(texto_audio, texto_doc)
            
            st.success("Análisis completado exitosamente.")
            st.markdown("---")
            st.markdown(resultado)
            
            if texto_audio:
                with st.expander("Ver Log de Transcripción"):
                    st.write(texto_audio)
