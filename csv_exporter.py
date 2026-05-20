def create_flashcards_csv(summary_text):
    """
    Parser Dinámico: Lee cualquier tabla generada, extrae los títulos de las columnas 
    y genera preguntas de Anki tabuladas (\t) automáticamente.
    """
    output = ""
    lines = summary_text.split('\n')
    in_table = False
    headers = []
    
    for line in lines:
        if line.strip().startswith('|') and line.strip().endswith('|'):
            # Ignorar separador
            if '---' in line:
                continue
                
            # Extraer columnas limpias
            cols = [col.strip().replace('**', '') for col in line.split('|')[1:-1]]
            
            if not in_table:
                # La primera fila que detecta son los encabezados (Headers)
                headers = cols
                in_table = True
            else:
                # Filas de datos
                if len(cols) == len(headers) and len(cols) > 1:
                    concepto_principal = cols[0]
                    
                    # Iterar sobre el resto de las columnas para crear las flashcards
                    for i in range(1, len(cols)):
                        dato = cols[i]
                        tipo_dato = headers[i]
                        
                        # Evitar generar tarjetas vacías si la IA puso N/E
                        if dato and dato.upper() != "N/E":
                            pregunta = f"¿Cuál es el/la {tipo_dato} correspondiente a: {concepto_principal}?"
                            output += f"{pregunta}\t{dato}\n"
        else:
            # Reseteamos al salir de una tabla
            in_table = False
            headers = []
            
    return output
