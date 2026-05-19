import streamlit as st
from doc_processor import process_documents
from asr_client import transcribe_media
from llm_client import process_with_llm
from word_exporter import create_word_document
from csv_exporter import create_flashcards_csv

# Configuración técnica de la página
st.set_page_config(
    page_title="Centro de Análisis Semántico Médico",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Estilización de cabecera profesional
st.title("👨‍⚕️ Sistema de Resúmenes y Auditoría Médica")
st.markdown("""
    **Motor de Inferencia:** Gemini 2.5 Flash | **Protocolo:** Validación Cruzada y Exportación High-Yield
    ---
""")

# Inicialización de estado para persistencia de datos (Memoria UI)
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
            help="Soporta video para extraer datos visuales clínicos."
        )
    with col2:
        st.subheader("📄 Referencia Bibliográfica (Ground Truth)")
        doc_files = st.file_uploader(
            "Carga guías o PPTX (.pdf, .pptx) [Múltiples permitidos]", 
            type=["pdf", "pptx"],
            accept_multiple_files=True,
            help="El motor auditará y corregirá la transcripción oral utilizando estos documentos."
        )

st.markdown("---")

# Pipeline de Ejecución
col_btn, col_reset = st.columns([1, 4])
with col_btn:
    ejecutar = st.button("🚀 Iniciar Análisis Clínico", type="primary", use_container_width=True)
with col_reset:
    if st.button("🧹 Limpiar Sistema", use_container_width=False):
        st.session_state.resumen_generado = None
        st.session_state.log_transcripcion = None
        st.rerun()

if ejecutar:
    if not media_file and not doc_files:
        st.error("Protocolo interrumpido: Se requiere al menos una fuente de datos.")
    else:
        try:
            # Reemplazo de st.spinner por st.status para mejor UX durante la inferencia
            with st.status("Iniciando pipeline de procesamiento...", expanded=True) as status:
                
                st.write("⏳ Extrayendo texto bibliográfico (Ground Truth)...")
                texto_doc = process_documents(doc_files) if doc_files else None
                
                st.write("🎙️ Procesando y transcribiendo archivos multimedia...")
                texto_media = transcribe_media(media_file) if media_file else None
                st.session_state.log_transcripcion = texto_media
                
                st.write("🧠 Ejecutando motor de inferencia semántica y auditoría cruzada...")
                st.write("*(Si el archivo es muy largo, el sistema aplicará pausas de seguridad automáticamente)*")
                st.session_state.resumen_generado = process_with_llm(texto_media, texto_doc)
                
                status.update(label="✅ Análisis y validación completados exitosamente", state="complete", expanded=False)
                
        except Exception as e:
            st.error(f"Falla crítica en el pipeline: {str(e)}")

# Despliegue de Resultados Persistentes y Exportación
if st.session_state.resumen_generado:
    tab1, tab2 = st.tabs(["📊 Reporte Clínico Auditado", "📜 Log de Extracción Bruta"])
    
    with tab1:
        # Renderizado del Markdown generado por el LLM
        st.markdown(st.session_state.resumen_generado)
        
        # Herramientas de Exportación Profesional
        st.divider()
        col_word, col_csv = st.columns(2)
        
        with col_word:
            word_file = create_word_document(st.session_state.resumen_generado)
            st.download_button(
                label="📄 Descargar Reporte (.docx)",
                data=word_file,
                file_name="analisis_clinico_ia.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True
            )
            
        with col_csv:
            csv_data = create_flashcards_csv(st.session_state.resumen_generado)
            st.download_button(
                label="🧠 Descargar Mazo Examen (.csv)",
                data=csv_data,
                file_name="flashcards_medicina.csv",
                mime="text/csv",
                use_container_width=True
            )
        
    with tab2:
        if st.session_state.log_transcripcion:
            st.text_area("Texto bruto extraído de la ponencia multimedia:", st.session_state.log_transcripcion, height=400)
        else:
            st.info("No hay datos multimedia en este análisis.")
