def create_flashcards_csv(summary_text):
    """
    Parser Dinámico para Anki: Lee la estructura de tablas verticales con 
    Ejes Dinámicos e independiza cada fila en preguntas dirigidas.
    Exporta en formato de texto plano (.txt) separado por tabulaciones (\t).
    """
    output = ""
    lines = summary_text.split('\n')
    current_patologia = ""
    
    for line in lines:
        line_str = line.strip()
        
        # 1. Identificar la patología/enfermedad activa en el bucle
        if line_str.startswith('## '):
            # Limpiamos asteriscos por si la IA resalta el título
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
                # Limpiamos la columna de la pregunta (Anverso)
                eje_clinico = cols[0].replace('**', '').replace('*', '').strip()
                
                # La columna de la respuesta (Reverso) mantiene los <br> para que 
                # Anki dibuje los saltos de línea correctamente en la tarjeta.
                contenido = cols[1].strip()
                
                # Descartar ejes que la IA haya marcado como "N/E" (vacíos de info)
                if contenido and contenido.upper() != "N/E":
                    # Limpiamos los asteriscos del contenido para una lectura limpia en Anki
                    contenido_limpio = contenido.replace('**', '').replace('*', '')
                    
                    # Formulación de la pregunta cruzando el Título con el Eje
                    pregunta = f"¿Cuál es el/la {eje_clinico} asociado/a a: {current_patologia}?"
                    
                    # Inyección en el formato nativo de Anki (Pregunta \t Respuesta \n)
                    output += f"{pregunta}\t{contenido_limpio}\n"
                    
    return output
