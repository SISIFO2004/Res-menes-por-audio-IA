import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="Diagnóstico de API", layout="wide")
st.title("Consola de Diagnóstico: Google Generative AI")

try:
    # Intento de autenticación
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    st.info("Autenticación exitosa. Consultando listado de modelos vinculados a la API Key...")
    
    # Consulta directa a los servidores de Google
    modelos_generativos = []
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            modelos_generativos.append(m.name)
            
    # Evaluación de resultados
    if not modelos_generativos:
        st.error("Fallo Crítico: La API Key es válida, pero el servidor devuelve una lista vacía de modelos. Esto requiere generar una nueva clave directamente desde aistudio.google.com verificando que no haya restricciones.")
    else:
        st.success("Modelos generativos detectados y autorizados para esta credencial:")
        for modelo in modelos_generativos:
            st.code(modelo)
            
except Exception as e:
    st.error(f"Error de ejecución en la capa de red: {str(e)}")
