import streamlit as st
import google.generativeai as genai
import streamlit_mermaid as st_mermaid
from PyPDF2 import PdfReader
import re

# --- CONFIGURACIÓN DE SEGURIDAD ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.error("⚠️ Configura la API KEY en los Secrets.")
    st.stop()

# --- INTERFAZ ESTILO AI STUDIO ---
st.set_page_config(page_title="WrAp It Pro - Studio", layout="wide")

# CSS para imitar la interfaz limpia de Google AI Studio
st.markdown("""
<style>
    /* Fondo y tipografía */
    .stApp { background-color: #FFFFFF; }
    .css-1d391kg { background-color: #F8F9FA; border-right: 1px solid #E0E0E0; }
    
    /* Títulos estilo Studio */
    .studio-title { font-family: 'Google Sans', Arial; color: #1A73E8; font-size: 24px; font-weight: 500; margin-bottom: 20px; }
    
    /* Botones y selectores */
    .stButton>button { border-radius: 4px; background-color: #1A73E8; color: white; border: none; font-weight: 500; }
    .stButton>button:hover { background-color: #1765C1; border: none; }
    
    /* Área de respuesta */
    .output-container { background-color: #F1F3F4; padding: 20px; border-radius: 8px; border: 1px solid #DADCE0; }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR (PANEL DE CONFIGURACIÓN IZQUIERDO) ---
with st.sidebar:
    st.markdown("<div class='studio-title'>🛡️📊 WrAp It Pro</div>", unsafe_allow_html=True)
    st.markdown("---")
    
    st.subheader("Configuración")
    model_choice = st.selectbox("Modelo", ["gemini-1.5-flash", "gemini-1.5-pro"])
    
    st.subheader("Instrucciones del Sistema")
    sys_prompt = st.text_area("System Instructions", 
        value="Eres un consultor experto. Analiza el PDF y genera diagramas Mermaid (graph LR o mindmap) y resúmenes ejecutivos.",
        height=150)
    
    st.markdown("---")
    uploaded_file = st.file_uploader("Documento Actual (PDF)", type="pdf")
    
    if uploaded_file:
        if 'pdf_text' not in st.session_state:
            reader = PdfReader(uploaded_file)
            st.session_state.pdf_text = "".join([p.extract_text() or "" for p in reader.pages])
        st.success("✅ Archivo cargado")

# --- ÁREA PRINCIPAL (WORKSPACE) ---
if not uploaded_file:
    st.markdown("""
    <div style='text-align: center; padding-top: 100px;'>
        <h2 style='color: #5F6368;'>Bienvenido a WrAp It Studio</h2>
        <p style='color: #80868B;'>Sube un PDF en el panel izquierdo para comenzar el análisis.</p>
    </div>
    """, unsafe_allow_html=True)
else:
    # Menú de herramientas estilo Pestañas de Studio
    tool = st.radio("Herramienta de Análisis", 
                    ["Resumen Ejecutivo", "Key Points", "Diagrama Ishikawa", "Mapa Conceptual", "Chat Consultor"],
                    horizontal=True)
    
    st.markdown("---")
    
    col_input, col_output = st.columns([1, 1.5])
    
    with col_input:
        st.markdown("**Prompt / Consulta**")
        if tool == "Chat Consultor":
            user_input = st.text_area("Pregunta algo sobre el documento...", height=200)
        else:
            user_input = st.text_area("Instrucciones adicionales (opcional)", 
                                    placeholder=f"Generando {tool} basado en el PDF...", height=200)
        
        run_btn = st.button("Ejecutar (Run)", type="primary")

    with col_output:
        st.markdown("**Resultado / Visualización**")
        if run_btn:
            with st.spinner("Procesando..."):
                # Lógica de prompts según herramienta
                prompts = {
                    "Resumen Ejecutivo": "Haz un resumen ejecutivo profesional de este texto: ",
                    "Key Points": "Extrae los puntos clave más importantes de: ",
                    "Diagrama Ishikawa": "Genera un diagrama de Ishikawa en formato mermaid graph LR de: ",
                    "Mapa Conceptual": "Genera un mapa conceptual en formato mermaid mindmap de: ",
                    "Chat Consultor": f"{user_input}. Basado en: "
                }
                
                final_prompt = prompts[tool] + st.session_state.pdf_text[:8000]
                
                model = genai.GenerativeModel(model_name=model_choice, system_instruction=sys_prompt)
                response = model.generate_content(final_prompt)
                
                # Mostrar texto
                st.markdown(f"<div class='output-container'>{response.text}</div>", unsafe_allow_html=True)
                
                # Renderizar Mermaid si existe
                m_code = re.search(r"```mermaid\s+(.*?)\s+```", response.text, re.DOTALL)
                if m_code:
                    st.markdown("---")
                    st_mermaid.st_mermaid(m_code.group(1), height="500px")
