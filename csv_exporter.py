def create_flashcards_csv(summary_text):
    """
    Parser Dinámico para Anki (Estilo High-Yield): 
    Lee la estructura de tablas verticales, traduce flechas lógicas 
    y genera flashcards directas y densas en datos.
    Exporta en formato de texto plano (.txt) separado por tabulaciones (\t).
    """
    output = ""
    lines = summary_text.split('\n')
    current_patologia = ""
    
    for line in lines:
        line_str = line.strip()
        
        # 1. Identificar la patología/enfermedad activa
        if line_str.startswith('## '):
            current_patologia = line_str.replace('## ', '').replace('**', '').strip()
            continue
            
        # 2. Interceptar las filas de la matriz
        if line_str.startswith('|') and line_str.endswith('|'):
            
            # Omitir cabeceras de control y líneas de formato Markdown
            if '---' in line_str or 'Eje Clínico' in line_str:
                continue
                
            # Extraer las dos columnas de la tabla vertical
            cols = [col.strip() for col in line_str.split('|')[1:-1]]
            
            if len(cols) >= 2 and current_patologia:
                # Eje clínico limpio (Anverso)
                eje_clinico = cols[0].replace('**', '').replace('*', '').strip()
                
                # Mantenemos los <br> para saltos de línea en Anki 
                # y traducimos las flechas lógicas para consistencia visual
                contenido = cols[1].strip().replace('-->', '→').replace('->', '→')
                
                # Descartar ejes vacíos ("N/E")
                if contenido and contenido.upper() != "N/E":
                    # Limpieza final de asteriscos Markdown
                    contenido_limpio = contenido.replace('**', '').replace('*', '')
                    
                    # Formulación de la pregunta directa (Estilo academia)
                    pregunta = f"¿{eje_clinico} de: {current_patologia}?"
                    
                    # Inyección en formato nativo Anki
                    output += f"{pregunta}\t{contenido_limpio}\n"
                    
    return output
