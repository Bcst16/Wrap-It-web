
    import streamlit as st
import google.generativeai as genai
import streamlit_mermaid as st_mermaid
from PyPDF2 import PdfReader
import re

# --- SEGURIDAD ---
try:
    raw_key = st.secrets["GOOGLE_API_KEY"]
    clean_key = raw_key.strip().replace('"', '').replace("'", "")
    genai.configure(api_key=clean_key)
except Exception:
    st.error("⚠️ Error: Revisa los Secrets en Streamlit Cloud.")
    st.stop()

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="WrAp It", page_icon="🧠", layout="wide")

# CSS PARA ELIMINAR EL FONDO BLANCO TOTAL
st.markdown("""
<style>
    /* 1. Fondo general de la App: Gris suave corporativo */
    .stApp { background-color: #F0F2F5; }
    
    /* 2. Sidebar: Un tono más oscuro para contraste lateral */
    [data-testid="stSidebar"] { 
        background-color: #E5E7EB !important; 
        border-right: 1px solid #D1D5DB; 
    }
    
    /* 3. Tarjetas de Contenido: Blanco puro con sombra suave para que 'floten' */
    .content-card { 
        background-color: #FFFFFF; 
        border-radius: 12px; 
        padding: 25px; 
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        border: 1px solid #E5E7EB;
        margin-bottom: 20px;
    }

    /* Ajuste de márgenes y títulos */
    .block-container { padding: 2rem 4rem; max-width: 98% !important; }
    h2, h3 { color: #1F2937; font-weight: 700; }
    
    /* Botones de herramientas */
    .stRadio > div { gap: 10px; }
    .stRadio label { 
        background-color: #FFFFFF; border: 1px solid #D1D5DB; padding: 10px 15px; 
        border-radius: 8px; width: 100%; transition: 0.2s; font-weight: 600;
    }
    .stRadio label:hover { border-color: #1A73E8; background-color: #F9FAFB; }
</style>
""", unsafe_allow_html=True)

# --- PANEL LATERAL ---
with st.sidebar:
    # Logo Centralizado
    st.markdown("<div style='text-align: center; margin-bottom: 20px;'>", unsafe_allow_html=True)
    logo_url = "https://raw.githubusercontent.com/Bcst16/Wrap-it-web/main/logo.png"
    st.image(logo_url, width=220)
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("### Herramientas")
    tool = st.radio("Acción:", ["Dashboard", "Resumen Ejecutivo", "Key Points", "Ishikawa", "Mapa Conceptual"], label_visibility="collapsed")
    
    st.markdown("---")
    uploaded_file = st.file_uploader("Documento PDF", type="pdf")
    if uploaded_file:
        if 'pdf_text' not in st.session_state:
            reader = PdfReader(uploaded_file)
            st.session_state.pdf_text = "".join([p.extract_text() or "" for p in reader.pages])
        st.success("✅ Archivo Listo")

# --- ÁREA PRINCIPAL ---
if not uploaded_file:
    st.markdown("<div style='text-align:center; margin-top:150px;'><h2 style='color:#6B7280;'>Sube un PDF para activar el análisis</h2></div>", unsafe_allow_html=True)
else:
    st.markdown(f"## {tool}")
    
    col_in, col_out = st.columns([1, 1.5], gap="large")
    
    with col_in:
        # Usamos la clase 'content-card' para que resalte del fondo gris
        st.markdown("<div class='content-card'>", unsafe_allow_html=True)
        st.markdown("**Instrucciones adicionales**")
        user_input = st.text_area("Ej: Resume solo la parte financiera...", height=150, label_visibility="collapsed")
        run_btn = st.button("PROCESAR ANÁLISIS", type="primary")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_out:
        if run_btn:
            with st.spinner("Generando..."):
                prompts = {
                    "Dashboard": "Resumen ejecutivo y mapa conceptual de: ",
                    "Resumen Ejecutivo": "Resumen ejecutivo detallado de: ",
                    "Key Points": "Extrae los 5 puntos clave de: ",
                    "Ishikawa": "Diagrama Ishikawa (mermaid graph LR) de: ",
                    "Mapa Conceptual": "Mapa conceptual (mermaid mindmap) de: "
                }
                model = genai.GenerativeModel("gemini-1.5-flash")
                response = model.generate_content(prompts[tool] + st.session_state.pdf_text[:8500])
                
                # Resultado en tarjeta blanca
                st.markdown("<div class='content-card'>", unsafe_allow_html=True)
                st.markdown(response.text)
                st.markdown("</div>", unsafe_allow_html=True)
                
                m_code = re.search(r"```mermaid\s+(.*?)\s+```", response.text, re.DOTALL)
                if m_code:
                    st.markdown("<div class='content-card'>", unsafe_allow_html=True)
                    st_mermaid.st_mermaid(m_code.group(1), height="550px")
                    st.markdown("</div>", unsafe_allow_html=True)
