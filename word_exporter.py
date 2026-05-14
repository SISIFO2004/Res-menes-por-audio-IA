from docx import Document
from io import BytesIO

def create_word_document(summary_text):
    """
    Convierte el texto del resumen en un archivo .docx estructurado.
    """
    doc = Document()
    doc.add_heading('Resumen Médico - Análisis de IA', 0)
    
    lines = summary_text.split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Mapeo básico de Markdown a estilos de Word
        if line.startswith('### '):
            doc.add_heading(line.replace('### ', ''), level=2)
        elif line.startswith('## '):
            doc.add_heading(line.replace('## ', ''), level=1)
        elif line.startswith('* ') or line.startswith('- '):
            # Limpiar viñeta y añadir párrafo con estilo de lista
            clean_text = line.replace('* ', '').replace('- ', '')
            doc.add_paragraph(clean_text, style='List Bullet')
        else:
            doc.add_paragraph(line)
            
    # Guardar en un buffer de memoria para Streamlit
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer
