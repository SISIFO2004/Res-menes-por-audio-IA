from docx import Document
from io import BytesIO

def create_word_document(summary_text):
    """
    Convierte el texto del resumen (Markdown) en un archivo .docx estructurado,
    procesando nativamente tablas, títulos y limpiando etiquetas de formato.
    """
    doc = Document()
    doc.add_heading('Reporte Clínico Auditado - IA', 0)
    
    lines = summary_text.split('\n')
    
    in_table = False
    table = None
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Limpiamos los asteriscos de Markdown para que no se vean en Word
        clean_line = line.replace('**', '')
            
        # 1. DETECCIÓN DE TABLAS MARKDOWN
        if clean_line.startswith('|') and clean_line.endswith('|'):
            # Ignorar la línea separadora de formato Markdown (|---|---|)
            if '---' in clean_line:
                continue
                
            # Extraer el contenido de las celdas (ignorando los bordes vacíos del split)
            celdas = clean_line.split('|')[1:-1]
            celdas = [c.strip() for c in celdas]
            
            # Si apenas entramos a la tabla, creamos la cabecera
            if not in_table:
                in_table = True
                # Crear tabla en Word con estilo de cuadrícula visible
                table = doc.add_table(rows=1, cols=len(celdas))
                table.style = 'Table Grid'
                
                # Rellenar primera fila (Cabecera)
                hdr_cells = table.rows[0].cells
                for i, texto in enumerate(celdas):
                    if i < len(hdr_cells):
                        hdr_cells[i].text = texto
            else:
                # Agregar fila de datos subsecuente
                row_cells = table.add_row().cells
                for i, texto in enumerate(celdas):
                    if i < len(row_cells):
                        row_cells[i].text = texto
            continue
        else:
            in_table = False # Resetea el estado si ya no hay barras '|'
            
        # 2. PROCESAMIENTO DE TEXTO ESTÁNDAR
        if clean_line.startswith('### '):
            doc.add_heading(clean_line.replace('### ', ''), level=2)
        elif clean_line.startswith('## '):
            doc.add_heading(clean_line.replace('## ', ''), level=1)
        elif clean_line.startswith('* ') or clean_line.startswith('- '):
            # Formato de lista con viñeta
            texto_lista = clean_line.replace('* ', '', 1).replace('- ', '', 1)
            doc.add_paragraph(texto_lista, style='List Bullet')
        else:
            doc.add_paragraph(clean_line)
            
    # Guardar en un buffer de memoria para Streamlit
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer
