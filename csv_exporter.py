def create_flashcards_csv(summary_text):
    """
    Analiza el texto de salida del LLM y genera un formato de texto plano (.txt) 
    separado por tabulaciones (\t), el cual es el formato nativo infalible para Anki.
    """
    output = ""
    lines = summary_text.split('\n')
    in_table = False
    
    for line in lines:
        # Detectamos el inicio de la tabla
        if 'Patología / Concepto' in line and '|' in line:
            in_table = True
            continue
            
        if in_table and '---' in line:
            continue # Omitimos línea de formato
            
        if in_table and line.strip().startswith('|'):
            # Limpiamos las columnas
            cols = [col.strip() for col in line.split('|') if col.strip()]
            
            if len(cols) >= 4:
                # Limpiar asteriscos Markdown
                patologia = cols[0].replace('**', '').strip()
                clinica = cols[1].replace('**', '').strip()
                dx = cols[2].replace('**', '').strip()
                tx = cols[3].replace('**', '').strip()
                
                # ==== FORMULACIÓN MODO PROFESOR (Separado por \t) ====
                if clinica != "N/E":
                    q_clin = f"🩺 Clínica: ¿Cuál es la presentación característica o signos clave en: {patologia}?"
                    output += f"{q_clin}\t{clinica}\n"
                    
                if dx != "N/E":
                    q_dx = f"🔬 Diagnóstico: Ante la sospecha de {patologia}, ¿cuál es el abordaje inicial o Gold Standard?"
                    output += f"{q_dx}\t{dx}\n"
                    
                if tx != "N/E":
                    q_tx = f"💊 Tratamiento: ¿Cuál es la primera línea de manejo indicada para {patologia}?"
                    output += f"{q_tx}\t{tx}\n"
                    
        # Si la línea está vacía y ya estábamos en la tabla, cerramos el escaneo
        elif in_table and not line.strip():
            in_table = False
            
    return output
