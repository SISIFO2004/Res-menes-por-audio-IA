from docx import Document
from io import BytesIO

def create_word_document(summary_text):
    """
    Convierte el reporte de la IA en fichas estructuradas de Word en orientación 
    vertical. Procesa tablas bidimensionales de manera limpia y traduce las 
    viñetas internas (<br>) en formatos nativos de lista de Microsoft Word.
    """
    doc = Document()
    
    # Encabezado principal del documento institucional
    doc.add_heading('Fichas de Estudio Clínico - High-Yield', 0)
    
    lines = summary_text.split('\n')
    in_table = False
    table = None
    
    for line in lines:
        line_str = line.strip()
        if not line_str:
            continue
            
        # =====================================================================
        # 1. DETECCIÓN Y PROCESAMIENTO DE MATRICES (TABLAS)
        # =====================================================================
        if line_str.startswith('|') and line_str.endswith('|'):
            if '---' in line_str:
                continue # Omitir líneas de formato estético de Markdown
                
            # Separar las columnas limpiando espacios sobrantes
            celdas = [c.strip() for c in line_str.split('|')[1:-1]]
            
            if not in_table:
                # Inicialización de la cabecera del cuadro clínico
                in_table = True
                table = doc.add_table(rows=0, cols=len(celdas))
                table.style = 'Table Grid'
                
                row = table.add_row()
                for i, cell_text in enumerate(celdas):
                    clean_text = cell_text.replace('**', '').replace('*', '').strip()
                    cell = row.cells[i]
                    p = cell.paragraphs[0]
                    run = p.add_run(clean_text)
                    run.bold = True # Cabecera en negrita obligatoria
            else:
                # Inyección de filas de contenido clínico (Eje vs Datos)
                row = table.add_row()
                for i, cell_text in enumerate(celdas):
                    cell = row.cells[i]
                    p = cell.paragraphs[0]
                    
                    # Segmentar el contenido por saltos de línea lógicos (<br> o \n)
                    partes = cell_text.replace('<br>', '\n').split('\n')
                    
                    for idx, parte in enumerate(partes):
                        parte_limpia = parte.strip()
                        if not parte_limpia:
                            continue
                            
                        # Si la celda ya tiene contenido previo, creamos un párrafo subordinado
                        if idx > 0 or p.text:
                            p = cell.add_paragraph()
                            
                        # Traducir viñetas de texto a estilos nativos de Microsoft Word
                        if parte_limpia.startswith('- ') or parte_limpia.startswith('* '):
                            p.style = 'List Bullet'
                            texto_final = parte_limpia[2:].strip()
                        else:
                            texto_final = parte_limpia
                            
                        # Purgar residuos de marcadores Markdown (** o *)
                        texto_final_limpio = texto_final.replace('**', '').replace('*', '')
                        run = p.add_run(texto_final_limpio)
                        
                        # Forzar negrita en la primera columna (Eje Clínico) para contraste visual
                        if i == 0:
                            run.bold = True
            continue
        else:
            # Al salir del flujo de la tabla, restablecer el estado del cursor
            in_table = False
            
        # =====================================================================
        # 2. PROCESAMIENTO DE TÍTULOS Y SECCIONES AUTÓNOMAS
        # =====================================================================
        if line_str.startswith('### '):
            doc.add_heading(line_str.replace('### ', '').replace('**', '').strip(), level=2)
        elif line_str.startswith('## '):
            doc.add_heading(line_str.replace('## ', '').replace('**', '').strip(), level=1)
        elif line_str.startswith('# '):
            doc.add_heading(line_str.replace('# ', '').replace('**', '').strip(), level=0)
        else:
            # Párrafos de texto convencionales limpios de marcas analíticas
            p_text = line_str.replace('**', '').replace('*', '').strip()
            doc.add_paragraph(p_text)
            
    # Compilación en el buffer temporal de memoria RAM para la descarga en Streamlit
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer
