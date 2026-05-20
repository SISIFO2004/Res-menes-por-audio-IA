from docx import Document
from docx.enum.section import WD_ORIENT
from io import BytesIO

def create_word_document(summary_text):
    """
    Convierte las tablas Markdown a un archivo .docx en formato HORIZONTAL (Landscape)
    ideal para sábanas de estudio y cuadros de alto rendimiento.
    """
    doc = Document()
    
    # Configuración de página a Horizontal (Apaisado) para tablas anchas
    section = doc.sections[0]
    new_width, new_height = section.page_height, section.page_width
    section.orientation = WD_ORIENT.LANDSCAPE
    section.page_width = new_width
    section.page_height = new_height
    
    doc.add_heading('Sábana de Estudio Clínico - IA', 0)
    
    lines = summary_text.split('\n')
    in_table = False
    table = None
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        clean_line = line.replace('**', '')
            
        # PROCESAMIENTO DE TABLAS
        if clean_line.startswith('|') and clean_line.endswith('|'):
            if '---' in clean_line:
                continue
                
            celdas = clean_line.split('|')[1:-1]
            celdas = [c.strip() for c in celdas]
            
            if not in_table:
                in_table = True
                table = doc.add_table(rows=1, cols=len(celdas))
                table.style = 'Table Grid'
                
                hdr_cells = table.rows[0].cells
                for i, texto in enumerate(celdas):
                    if i < len(hdr_cells):
                        hdr_cells[i].text = texto
            else:
                row_cells = table.add_row().cells
                for i, texto in enumerate(celdas):
                    if i < len(row_cells):
                        row_cells[i].text = texto
            continue
        else:
            in_table = False 
            
        # PROCESAMIENTO DE TÍTULOS
        if clean_line.startswith('### '):
            doc.add_heading(clean_line.replace('### ', ''), level=2)
        elif clean_line.startswith('## '):
            doc.add_heading(clean_line.replace('## ', ''), level=1)
        else:
            doc.add_paragraph(clean_line)
            
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer
