import streamlit as st
import google.generativeai as genai
import streamlit_mermaid as st_mermaid
from PyPDF2 import PdfReader
import re

# --- CONFIGURACIÓN DE SEGURIDAD (AJUSTADA) ---
# Aquí es donde ocurre la magia: ya no ponemos la llave entre comillas.
# La app la buscará en la configuración de Streamlit Cloud.
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.error("⚠️ Error: No se encontró la API KEY en los Secrets de Streamlit.")

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="WrAp It", page_icon="📝", layout="wide")

st.markdown("<h1 style='text-align: center; color: #6C63FF;'>📝 WrAp It</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Análisis Pedagógico, Corporativo e Interactivo</p>", unsafe_allow_html=True)

# --- SYSTEM INSTRUCTION (INGLÉS PARA PRECISIÓN) ---
SYSTEM_PROMPT = """
Role: You are "WrAp It", an expert in visual data deconstruction.
Instructions:
1. Analysis: Use bullet points for text summaries.
2. Visuals: Use ONLY Mermaid.js syntax. 
   - Mind Maps: use `mindmap` syntax.
   - Ishikawa: use `graph LR` to create a fishbone (Causes -> Effect).
3. CRITICAL: Always wrap Mermaid code between ```mermaid and ``` blocks.
4. Language: Respond in Spanish.
"""

def extract_pdf_text(pdf_file):
    reader = PdfReader(pdf_file)
    return "".join([page.extract_text() or "" for page in reader.pages])

def find_mermaid_code(text):
    match = re.search(r"```mermaid\s+(.*?)\s+```", text, re.DOTALL)
    return match.group(1) if match else None

# --- INTERFAZ ---
with st.sidebar:
    st.header("📂 Documento")
    uploaded_file = st.file_uploader("Sube tu PDF", type="pdf")

if uploaded_file:
    full_text = extract_pdf_text(uploaded_file)
    st.success("✅ PDF cargado.")

    col1, col2 = st.columns(2)
    with col1: btn_ishikawa = st.button("🐟 Diagrama Ishikawa")
    with col2: btn_mapa = st.button("🧠 Mapa Conceptual")

    query = ""
    if btn_ishikawa: query = f"Analiza los problemas de este texto y genera un diagrama de Ishikawa en formato mermaid: {full_text[:6000]}"
    elif btn_mapa: query = f"Crea un mapa mental detallado en formato mermaid de este texto: {full_text[:6000]}"

    if query:
        with st.spinner("Analizando con Gemini..."):
            model = genai.GenerativeModel(model_name="gemini-1.5-flash", system_instruction=SYSTEM_PROMPT)
            response = model.generate_content(query)
            
            res_col, map_col = st.columns([1, 1.2])
            with res_col:
                st.subheader("Análisis")
                st.markdown(response.text)
            with map_col:
                m_code = find_mermaid_code(response.text)
                if m_code:
                    st.subheader("Visualización Interactiva")
                    st_mermaid.st_mermaid(m_code, height="500px")
else:
    st.info("Sube un PDF para comenzar.")
