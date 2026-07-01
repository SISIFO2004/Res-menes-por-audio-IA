import streamlit as st
import PyPDF2

# Importaciones de los módulos de tu sistema
from llm_client import process_with_llm
from word_exporter import create_word_document
from csv_exporter import create_flashcards_csv
from asr_client import transcribe_media  # Integración real de tu módulo de audio

# Configuración de la página
st.set_page_config(
    page_title="Generador de Fichas Clínicas",
    page_icon="⚕️",
    layout="wide"
)

# Interfaz Principal
st.title("⚕️ Sistema de Fichas Clínicas Autogestionado")
st.markdown("Sube el audio de tu clase y tu bibliografía para generar matrices de estudio y tarjetas de Anki.")

# Contenedores de entrada de datos (Uploaders)
col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Ponencia Oral (Audio/Video)")
    archivo_audio = st.file_uploader(
        "Carga el archivo multimedia de la clase:", 
        type=["mp3", "wav", "m4a", "ogg", "mp4"]
    )

with col2:
    st.subheader("2. Material Bibliográfico (PDF)")
    archivo_pdf = st.file_uploader(
        "Carga el documento de referencia (PDF):", 
        type=["pdf"]
    )

# La caja de inyección de prompt dinámico
st.subheader("3. Instrucciones Especiales para la IA (Opcional)")
instrucciones_extra = st.text_area(
    "🧠 Escribe tu directiva personalizada aquí:",
    height=100,
    placeholder="Ej. 'Resume solo los tratamientos de primera línea', 'Omite la fisiopatología', 'Hazlo extremadamente corto'. Si lo dejas vacío, el sistema hará el análisis tabular completo."
)

# Botón de ejecución
if st.button("Generar Fichas de Estudio", use_container_width=True):
    if not archivo_audio and not archivo_pdf:
        st.warning("⚠️ Debes cargar al menos un archivo (Audio o PDF) para iniciar el análisis.")
    else:
        with st.spinner("Procesando archivos y estructurando matrices clínicas... Esto puede tardar varios minutos debido al análisis del audio."):
            
            texto_media = ""
            texto_doc = ""
            
            # 1. Procesamiento del Audio usando asr_client.py
            if archivo_audio is not None:
                st.info("Transcribiendo y analizando el contenido multimedia...")
                texto_media = transcribe_media(archivo_audio)
                
                if "Error" in texto_media:
                    st.error(texto_media)
                    st.stop()  # Detiene la ejecución si falla el audio
            
            # 2. Procesamiento del PDF
            if archivo_pdf is not None:
                st.info("Extrayendo texto de la bibliografía...")
                try:
                    lector_pdf = PyPDF2.PdfReader(archivo_pdf)
                    for pagina in lector_pdf.pages:
                        texto_extraido = pagina.extract_text()
                        if texto_extraido:
                            texto_doc += texto_extraido + "\n"
                except Exception as e:
                    st.error(f"Error al procesar el archivo PDF: {str(e)}")
                    st.stop()
            
            # 3. Llamada al motor de inferencia (LLM)
            st.info("Estructurando matrices de conocimiento clínico...")
            resultado_md = process_with_llm(texto_media, texto_doc, instrucciones_extra)
            
            # Manejo de errores de la API en el modelo principal
            if "Error" in resultado_md or "⚠️" in resultado_md:
                st.error(resultado_md)
            else:
                st.success("¡Análisis completado con éxito!")
                
                # Renderizado de la previsualización en la web
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
