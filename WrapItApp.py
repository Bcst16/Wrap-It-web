import streamlit as st
import google.generativeai as genai
import streamlit_mermaid as st_mermaid
from PyPDF2 import PdfReader
import re

# --- SEGURIDAD ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.error("⚠️ Error: Configura la API KEY en los Secrets.")
    st.stop()

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="WrAp It", page_icon="🧠", layout="wide")

# CSS PARA ESTILO ELITE (MÁXIMA LIMPIEZA)
st.markdown("""
<style>
    .block-container { padding-top: 1.5rem; max-width: 95% !important; }
    .stApp { background-color: #FFFFFF; }
    [data-testid="stSidebar"] { background-color: #F8F9FA; border-right: 1px solid #E5E7EB; width: 320px !important; }
    
    /* Contenedor del Logo */
    .logo-container { text-align: center; margin-bottom: 2rem; }
    
    /* Botones de Navegación */
    .stRadio > div { gap: 10px; }
    .stRadio label { 
        background-color: #FFFFFF; border: 1px solid #E5E7EB; padding: 12px 15px; 
        border-radius: 8px; width: 100%; transition: 0.2s; font-weight: 500;
    }
    .stRadio label:hover { border-color: #1A73E8; background-color: #F1F7FE; }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR CON LOGO OFICIAL ---
with st.sidebar:
    st.markdown("<div class='logo-container'>", unsafe_allow_html=True)
    # Jalamos la imagen directamente de tu GitHub
    st.image("https://raw.githubusercontent.com/Bcst16/Wrap-it-web/main/logo_final.png", width=250)
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("### Herramientas")
    tool = st.radio("Acción:", ["📊 Dashboard", "📝 Resumen", "📍 Key Points", "🐟 Ishikawa", "🧠 M. Conceptual"], label_visibility="collapsed")
    
    st.markdown("---")
    uploaded_file = st.file_uploader("Documento PDF", type="pdf")
    
    if uploaded_file:
        if 'pdf_text' not in st.session_state:
            reader = PdfReader(uploaded_file)
            st.session_state.pdf_text = "".join([p.extract_text() or "" for p in reader.pages])
        st.success("✅ Sistema Listo")

# --- ÁREA DE TRABAJO ---
if not uploaded_file:
    st.markdown("<div style='text-align:center; margin-top:120px;'><h2 style='color:#9CA3AF;'>Bienvenido. Sube un PDF para inicializar WrAp It.</h2></div>", unsafe_allow_html=True)
else:
    st.markdown(f"## {tool}")
    col_in, col_out = st.columns([1, 1], gap="large")
    
    with col_in:
        st.markdown("**Configuración del Análisis**")
        user_input = st.text_area("Instrucciones adicionales:", height=150, placeholder="Ej: Enfócate en los objetivos estratégicos...")
        run_btn = st.button("EJECUTAR PROCESO", type="primary")
        
    with col_out:
        st.markdown("**Resultado e Inteligencia**")
        if run_btn:
            with st.spinner("Procesando con Gemini 1.5..."):
                prompts = {
                    "📊 Dashboard": "Resumen ejecutivo y mapa mental de: ",
                    "📝 Resumen": "Resumen ejecutivo de alta gerencia de: ",
                    "📍 Key Points": "Hallazgos clave de: ",
                    "🐟 Ishikawa": "Diagrama Ishikawa (causa-raíz) en mermaid graph LR de: ",
                    "🧠 M. Conceptual": "Mapa conceptual en mermaid mindmap de: "
                }
                model = genai.GenerativeModel("gemini-1.5-flash")
                response = model.generate_content(prompts[tool] + st.session_state.pdf_text[:9000])
                
                st.write(response.text)
                m_code = re.search(r"```mermaid\s+(.*?)\s+```", response.text, re.DOTALL)
                if m_code:
                    st.markdown("---")
                    st_mermaid.st_mermaid(m_code.group(1), height="550px")
