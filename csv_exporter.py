import csv
import io

def create_flashcards_csv(summary_text):
    """
    Analiza el texto de salida del LLM, intercepta la tabla Markdown,
    y formulan preguntas tipo examen (Anverso/Reverso) exportables.
    """
    output = io.StringIO()
    # Usamos formato genérico CSV compatible con Anki
    writer = csv.writer(output, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    writer.writerow(['Pregunta (Anverso)', 'Respuesta (Reverso)'])
    
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
                # Limpiar asteriscos Markdown para mejor lectura
                patologia = cols[0].replace('**', '').strip()
                clinica = cols[1].replace('**', '').strip()
                dx = cols[2].replace('**', '').strip()
                tx = cols[3].replace('**', '').strip()
                
                # ==== FORMULACIÓN MODO PROFESOR ====
                if clinica != "N/E":
                    q_clin = f"🩺 Clínica: ¿Cuál es la presentación característica o signos clave en: {patologia}?"
                    writer.writerow([q_clin, clinica])
                    
                if dx != "N/E":
                    q_dx = f"🔬 Diagnóstico: Ante la sospecha de {patologia}, ¿cuál es el abordaje inicial o Gold Standard?"
                    writer.writerow([q_dx, dx])
                    
                if tx != "N/E":
                    q_tx = f"💊 Tratamiento: ¿Cuál es la primera línea de manejo indicada para {patologia}?"
                    writer.writerow([q_tx, tx])
                    
        # Si la línea está vacía y ya estábamos en la tabla, se acabó
        elif in_table and not line.strip():
            in_table = False
            
    output.seek(0)
    return output.getvalue()
