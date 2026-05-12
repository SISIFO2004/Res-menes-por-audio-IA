import streamlit as st
from doc_processor import process_document
from asr_client import transcribe_audio
from llm_client import process_with_llm

st.set_page_config(page_title="Resúmenes Médicos IA", page_icon="🩺", layout="wide")

st.title("Sistema de Resúmenes Médicos 100% Gratuito")
st.markdown("Procesamiento de audio y documentos mediante Google Gemini 1.5.")

col1, col2 = st.columns(2)
with col1:
    audio_file = st.file_uploader("Carga tu audio (Clase, ponencia)", type=["wav", "mp3", "m4a"])
with col2:
    doc_file = st.file_uploader("Carga bibliografía (PDF/PPTX)", type=["pdf", "pptx"])

if st.button("Generar Resumen Inteligente", type="primary"):
    if not audio_file and not doc_file:
        st.error("Sube al menos un archivo.")
    else:
        with st.spinner("Gemini está analizando tus archivos..."):
            texto_doc = process_document(doc_file) if doc_file else None
            texto_audio = transcribe_audio(audio_file) if audio_file else None
            
            resultado = process_with_llm(texto_audio, texto_doc)
            
            st.success("¡Análisis completado!")
            st.markdown("---")
            st.markdown(resultado)
            
            if texto_audio:
                with st.expander("Ver transcripción completa"):
                    st.write(texto_audio)
