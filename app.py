import streamlit as st
import PyPDF2
from io import BytesIO

# Importaciones de los módulos del sistema
from llm_client import process_with_llm
from word_exporter import create_word_document
from csv_exporter import create_flashcards_csv

# Configuración de la página
st.set_page_config(
    page_title="Generador de Fichas Clínicas",
    page_icon="⚕️",
    layout="wide"
)

# Interfaz Principal
st.title("⚕️ Sistema de Fichas Clínicas Autogestionado")
st.markdown("Procesa tus transcripciones y bibliografía para generar matrices de estudio y tarjetas de Anki.")

# Contenedores de entrada de datos
col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Ponencia Oral (Audio transcrito)")
    texto_media = st.text_area(
        "Pega aquí la transcripción de la clase:", 
        height=250,
        placeholder="Pega el texto de tu clase o apuntes aquí..."
    )

with col2:
    st.subheader("2. Material Bibliográfico (PDF)")
    archivo_pdf = st.file_uploader(
        "Sube el documento de referencia (PDF)", 
        type=["pdf"]
    )

# Inyección de directivas dinámicas
st.subheader("3. Instrucciones Especiales para el Análisis")
instrucciones_extra = st.text_area(
    "🧠 Directivas (Opcional)",
    placeholder="Ej. 'Resume solo los tratamientos de primera línea', 'Omite la fisiopatología para hacerlo corto', 'Céntrate estrictamente en los criterios diagnósticos'. Si lo dejas vacío, realizará el análisis tabular completo."
)

# Botón de ejecución
if st.button("Generar Fichas de Estudio", use_container_width=True):
    if not texto_media and not archivo_pdf:
        st.warning("⚠️ Debes proporcionar la transcripción de la ponencia o un documento PDF para iniciar el análisis.")
    else:
        with st.spinner("Procesando datos clínicos y estructurando matrices... Esto puede tomar un momento debido a los límites de la API."):
            texto_doc = ""
            
            # Extracción de texto del PDF 
            if archivo_pdf is not None:
                try:
                    lector_pdf = PyPDF2.PdfReader(archivo_pdf)
                    for pagina in lector_pdf.pages:
                        texto_extraido = pagina.extract_text()
                        if texto_extraido:
                            texto_doc += texto_extraido + "\n"
                except Exception as e:
                    st.error(f"Error al procesar el archivo PDF: {str(e)}")
            
            # Llamada al motor de inferencia (LLM)
            resultado_md = process_with_llm(texto_media, texto_doc, instrucciones_extra)
            
            # Manejo de errores de la API o visualización de resultados
            if "Error" in resultado_md or "⚠️" in resultado_md:
                st.error(resultado_md)
            else:
                st.success("¡Análisis completado con éxito!")
                
                # Renderizado de la previsualización en Streamlit
                st.markdown("---")
                st.markdown("### Vista Previa de las Fichas")
                st.markdown(resultado_md)
                st.markdown("---")
                
                # Generación en memoria de los archivos exportables
                word_buffer = create_word_document(resultado_md)
                csv_text = create_flashcards_csv(resultado_md)
                
                # Botones de Descarga
                st.markdown("### 📥 Descargar Materiales de Estudio")
                d_col1, d_col2 = st.columns(2)
                
                with d_col1:
                    st.download_button(
                        label="📄 Descargar Fichas en Word",
                        data=word_buffer,
                        file_name="Fichas_Estudio_Clinico.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        use_container_width=True
                    )
                    
                with d_col2:
                    st.download_button(
                        label="🗂️ Descargar Mazo Anki (.txt)",
                        data=csv_text,
                        file_name="Tarjetas_Anki.txt",
                        mime="text/plain",
                        use_container_width=True
                    )
