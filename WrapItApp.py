import streamlit as st
import google.generativeai as genai
import streamlit_mermaid as st_mermaid
from PyPDF2 import PdfReader
import re

# --- SEGURIDAD (RESET LIMPIO) ---
try:
    # Jalamos la llave y eliminamos espacios, comillas simples y dobles
    raw_key = st.secrets["GOOGLE_API_KEY"]
    clean_key = raw_key.strip().replace('"', '').replace("'", "")
    genai.configure(api_key=clean_key)
except Exception:
    st.error("⚠️ Error Crítico: Revisa los Secrets en Streamlit Cloud.")
    st.stop()

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="WrAp It", page_icon="🧠", layout="wide")

st.markdown("""
<style>
    .block-container { padding-top: 1.5rem; max-width: 95% !important; }
    .stApp { background-color: #FFFFFF; }
    [data-testid="stSidebar"] { background-color: #F8F9FA; border-right: 1px solid #E5E7EB; width: 320px !important; }
    .logo-container { text-align: center; margin-bottom: 2rem; padding: 10px; }
    
    .stRadio label { 
        background-color: #FFFFFF; border: 1px solid #E5E7EB; padding: 12px 15px; 
        border-radius: 8px; width: 100%; transition: 0.2s; font-weight: 600; color: #4B5563;
    }
    .stRadio label:hover { border-color: #1A73E8; background-color: #F1F7FE; }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("<div class='logo-container'>", unsafe_allow_html=True)
    # Esta URL ahora sí coincidirá cuando lo renombres a logo.png
    logo_url = "https://raw.githubusercontent.com/Bcst16/Wrap-it-web/main/logo.png"
    st.image(logo_url, width=240)
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("### Herramientas")
    tool = st.radio("Acción:", ["Dashboard", "Resumen Ejecutivo", "Key Points", "Ishikawa", "Mapa Conceptual"], label_visibility="collapsed")
    
    st.markdown("---")
    uploaded_file = st.file_uploader("Subir PDF", type="pdf")

if uploaded_file:
    if 'pdf_text' not in st.session_state:
        reader = PdfReader(uploaded_file)
        st.session_state.pdf_text = "".join([p.extract_text() or "" for p in reader.pages])

    st.markdown(f"## {tool}")
    col_in, col_out = st.columns([1, 1.5], gap="large")
    
    with col_in:
        user_input = st.text_area("Instrucciones adicionales (opcional):", height=150)
        run_btn = st.button("EJECUTAR ANÁLISIS", type="primary")
        
    with col_out:
        if run_btn:
            with st.spinner("Procesando..."):
                try:
                    prompts = {
                        "Dashboard": "Resumen ejecutivo y mapa mental de: ",
                        "Resumen Ejecutivo": "Resumen ejecutivo de alta gerencia de: ",
                        "Key Points": "5 puntos clave de: ",
                        "Ishikawa": "Diagrama Ishikawa en mermaid graph LR de: ",
                        "Mapa Conceptual": "Mapa conceptual en mermaid mindmap de: "
                    }
                    model = genai.GenerativeModel("gemini-1.5-flash")
                    # Enviamos un fragmento seguro de texto
                    response = model.generate_content(prompts[tool] + st.session_state.pdf_text[:8000])
                    st.markdown(f"<div style='background:#FFFFFF; border:1px solid #E5E7EB; padding:20px; border-radius:10px;'>{response.text}</div>", unsafe_allow_html=True)
                    
                    m_code = re.search(r"```mermaid\s+(.*?)\s+```", response.text, re.DOTALL)
                    if m_code:
                        st_mermaid.st_mermaid(m_code.group(1), height="500px")
                except Exception as e:
                    st.error(f"Error: {e}")
else:
    st.markdown("<div style='text-align:center; margin-top:120px;'><h2 style='color:#9CA3AF;'>Carga un PDF para activar WrAp It</h2></div>", unsafe_allow_html=True)
