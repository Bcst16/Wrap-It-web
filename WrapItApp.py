import streamlit as st
import google.generativeai as genai
import streamlit_mermaid as st_mermaid
from PyPDF2 import PdfReader
import re

# --- SEGURIDAD ---
try:
    # Jalamos la llave y eliminamos espacios, comillas simples y dobles
    raw_key = st.secrets["GOOGLE_API_KEY"]
    clean_key = raw_key.strip().replace('"', '').replace("'", "")
    genai.configure(api_key=clean_key)
except Exception:
    st.error("⚠️ Error Crítico: Revisa los Secrets en Streamlit Cloud.")
    st.stop()

# --- CONFIGURACIÓN DE PÁGINA (WIDE & BRANDED) ---
st.set_page_config(page_title="WrAp It", page_icon="🧠", layout="wide")

# CSS PARA DISEÑO PROFESIONAL CON ALTO CONTRASTE
st.markdown("""
<style>
    /* 1. Fondo de Página: Gris Neutro Ultra Claro */
    .stApp { background-color: #F9FAFB; }
    
    /* 2. Sidebar: Gris Suave con Separación Clara */
    [data-testid="stSidebar"] { 
        background-color: #F3F4F6 !important; 
        border-right: 1px solid #E5E7EB; 
        width: 300px !important; 
    }
    
    /* Reset de márgenes para maximizar espacio */
    .block-container { padding: 2rem 3rem; max-width: 100% !important; }
    
    /* Títulos Principales */
    .main-header { font-family: 'Inter', sans-serif; color: #111827; font-size: 32px; font-weight: 700; margin-bottom: 2rem; }
    .sub-title { color: #6B7280; font-size: 14px; margin-top: -1.5rem; margin-bottom: 2rem; text-transform: uppercase; letter-spacing: 1px; }

    /* 3. Contenedores de Contenido: Blanco Puro para resaltar */
    .content-card { 
        background: #FFFFFF; 
        border: 1px solid #E5E7EB; 
        border-radius: 12px; 
        padding: 24px; 
        box-shadow: 0 1px 3px rgba(0,0,0,0.05); 
        margin-top: 1rem;
        margin-bottom: 1rem;
    }

    /* Estilo de Botones de Herramientas */
    .stRadio > div { gap: 10px; }
    .stRadio label { 
        background-color: #FFFFFF; border: 1px solid #E5E7EB; padding: 12px 15px; 
        border-radius: 8px; width: 100%; transition: 0.2s; font-weight: 500; color: #374151;
    }
    .stRadio label:hover { border-color: #1A73E8; background-color: #F1F7FE; color: #1A73E8; }
</style>
""", unsafe_allow_html=True)

# --- PROMPT DEL SISTEMA ---
SYSTEM_PROMPT = "Eres WrAp It, un motor de análisis corporativo. Generas diagramas Mermaid (graph LR/mindmap) y síntesis ejecutivas precisas en español."

# --- SIDEBAR (NAVEGACIÓN) ---
with st.sidebar:
    st.markdown("<div class='main-header'>WrAp It</div>", unsafe_allow_html=True)
    st.markdown("<p class='sub-title'>Intelligence Engine</p>", unsafe_allow_html=True)
    
    # Jalamos tu logo oficial (Asegúrate de que se llame logo.png en GitHub)
    try:
        logo_url = "https://raw.githubusercontent.com/Bcst16/Wrap-it-web/main/logo.png"
        st.image(logo_url, width=220)
    except:
        st.warning("No se pudo cargar el logo.")
        
    st.markdown("### 🛠️ Herramientas")
    tool = st.radio("Acción:", ["📊 Dashboard", "📝 Resumen", "📍 Key Points", "🐟 Ishikawa", "🧠 M. Conceptual"], label_visibility="collapsed")
    
    st.markdown("---")
    uploaded_file = st.file_uploader("Subir PDF Actual", type="pdf")
    
    if uploaded_file:
        if 'pdf_text' not in st.session_state:
            with st.spinner("Indexando..."):
                reader = PdfReader(uploaded_file)
                st.session_state.pdf_text = "".join([p.extract_text() or "" for p in reader.pages])
        st.success("✅ Documento cargado")

# --- ÁREA PRINCIPAL (WORKSPACE) ---
if not uploaded_file:
    # Pantalla de bienvenida limpia
    st.markdown("<div style='text-align:center; margin-top:150px;'><h2 style='color:#9CA3AF;'>Cargue un PDF para comenzar el análisis</h2></div>", unsafe_allow_html=True)
else:
    # Título dinámico de la herramienta
    st.markdown(f"## {tool}")
    st.markdown("---")
    
    # Diseño de pantalla dividida 50/50
    col_in, col_out = st.columns([1, 1], gap="large")
    
    with col_in:
        st.markdown("**Instrucciones de Refinamiento (Opcional)**")
        # El text_area se integra en una "content-card" blanca
        with st.container():
            st.markdown("<div class='content-card'>", unsafe_allow_html=True)
            user_input = st.text_area("Ej: Enfócate en los riesgos...", height=150, placeholder="Escribe aquí si quieres guiar el análisis...")
            run_btn = st.button("PROCESAR", type="primary")
            st.markdown("</div>", unsafe_allow_html=True)

    with col_out:
        st.markdown("**Resultado del Análisis**")
        if run_btn:
            with st.spinner("Gemini analizando..."):
                prompts = {
                    "📊 Dashboard": "Resumen ejecutivo y mapa mental de: ",
                    "📝 Resumen": "Resumen ejecutivo de alta gerencia de: ",
                    "📍 Key Points": "Los 5 hallazgos clave de: ",
                    "🐟 Ishikawa": "Ishikawa (causa-raíz) en mermaid graph LR de: ",
                    "🧠 M. Conceptual": "Mapa conceptual estructurado en mermaid mindmap de: "
                }
                
                # Combinamos el prompt con el texto del PDF y el input del usuario
                contexto = prompts[tool] + st.session_state.pdf_text[:9000]
                if user_input:
                    contexto += f". Consideración especial: {user_input}"
                
                model = genai.GenerativeModel("gemini-1.5-flash", system_instruction=SYSTEM_PROMPT)
                response = model.generate_content(contexto)
                
                # Tarjeta de resultado de texto (Blanca Puro)
                st.markdown(f"<div class='content-card'>{response.text}</div>", unsafe_allow_html=True)
                
                # Renderizado de Diagramas Mermaid
                m_code = re.search(r"```mermaid\s+(.*?)\s+```", response.text, re.DOTALL)
                if m_code:
                    st.markdown("---")
                    st.markdown("### Visualización")
                    # El diagrama también va en una tarjeta blanca
                    with st.container():
                        st.markdown("<div class='content-card'>", unsafe_allow_html=True)
                        st_mermaid.st_mermaid(m_code.group(1), height="600px")
                        st.markdown("</div>", unsafe_allow_html=True)
