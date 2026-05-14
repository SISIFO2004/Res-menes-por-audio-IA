import streamlit as st
from doc_processor import process_document
from asr_client import transcribe_media
from llm_client import process_with_llm
from word_exporter import create_word_document

# Configuración técnica de la página
st.set_page_config(
    page_title="Centro de Análisis Semántico Médico",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Estilización de cabecera profesional
st.title("👨‍⚕️ Sistema de Resúmenes Médicos")
st.markdown("""
    **Motor de Inferencia:** Gemini 2.5 Flash | **Protocolo:** Análisis Multimodal (Audio/Video/Doc)
    ---
""")

# Inicialización de estado para persistencia de datos
if 'resumen_generado' not in st.session_state:
    st.session_state.resumen_generado = None
if 'log_transcripcion' not in st.session_state:
    st.session_state.log_transcripcion = None

# Zona de Carga de Matrices de Datos
with st.container():
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📁 Ingesta Multimedia")
        media_file = st.file_uploader(
            "Carga la ponencia (.wav, .mp3, .m4a, .mp4)", 
            type=["wav", "mp3", "m4a", "mp4"],
            help="Soporta video para extraer datos de diapositivas."
        )
    with col2:
        st.subheader("📄 Referencia Bibliográfica")
        doc_file = st.file_uploader(
            "Carga guías o PPTX (.pdf, .pptx)", 
            type=["pdf", "pptx"],
            help="Proporciona el contexto 'Ground Truth' para evitar alucinaciones."
        )

st.markdown("---")

# Pipeline de Ejecución
col_btn, col_reset = st.columns([1, 4])
with col_btn:
    ejecutar = st.button("🚀 Iniciar Análisis", type="primary", use_container_width=True)
with col_reset:
    if st.button("🧹 Limpiar Sistema", use_container_width=False):
        st.session_state.resumen_generado = None
        st.session_state.log_transcripcion = None
        st.rerun()

if ejecutar:
    if not media_file and not doc_file:
        st.error("Protocolo interrumpido: Se requiere al menos una fuente de datos.")
    else:
        try:
            with st.spinner("Ejecutando inferencia semántica y visual..."):
                # 1. Procesamiento de Documento
                texto_doc = process_document(doc_file) if doc_file else None
                
                # 2. Procesamiento Multimedia
                texto_media = transcribe_media(media_file) if media_file else None
                st.session_state.log_transcripcion = texto_media
                
                # 3. Generación de Resumen Estructurado
                st.session_state.resumen_generado = process_with_llm(texto_media, texto_doc)
                
                st.success("Análisis completado exitosamente.")
        except Exception as e:
            st.error(f"Falla en el pipeline: {str(e)}")

# Despliegue de Resultados Persistentes
if st.session_state.resumen_generado:
    tab1, tab2 = st.tabs(["📊 Resumen Estructurado", "📜 Log de Extracción"])
    
    with tab1:
        st.markdown(st.session_state.resumen_generado)
        
        # Herramientas de Exportación Profesional
        st.divider()
        word_file = create_word_document(st.session_state.resumen_generado)
        st.download_button(
            label="⬇️ Descargar Reporte (.docx)",
            data=word_file,
            file_name="analisis_clinico_ia.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True
        )
        
    with tab2:
        if st.session_state.log_transcripcion:
            st.text_area("Texto bruto extraído:", st.session_state.log_transcripcion, height=400)
        else:
            st.info("No hay datos multimedia en este análisis.")
