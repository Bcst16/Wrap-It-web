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
    st.error("⚠️ Error: Configura la API KEY en los Secrets de Streamlit Cloud.")
    st.stop()

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="WrAp It Pro", page_icon="🛡️📊", layout="wide")

st.markdown("""
<style>
    .main-title { font-size: 42px; font-weight: bold; color: #1E3A8A; text-align: center; }
    .stButton>button { width: 100%; border-radius: 12px; height: 3.5em; background-color: #1E3A8A; color: white; font-weight: bold; border: none; }
    .stButton>button:hover { background-color: #3B82F6; color: white; transition: 0.3s; transform: scale(1.02); }
    .chat-container { background-color: #F8FAFC; padding: 20px; border-radius: 15px; border-left: 6px solid #1E3A8A; }
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='main-title'>🛡️📊 WrAp It Pro</div>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #6B7280;'>Consultoría Inteligente y Deconstrucción de Datos</p>", unsafe_allow_html=True)

# --- PROMPT DEL SISTEMA ---
SYSTEM_PROMPT = """Eres "WrAp It Pro", un consultor experto.
1. Herramientas Visuales: Usa Mermaid (graph LR para Ishikawa, mindmap para mapas).
2. Chat: Responde preguntas específicas sobre el PDF con tono profesional y directo.
3. Formato: Usa viñetas y negritas para resaltar puntos clave."""

def extract_text(pdf_file):
    reader = PdfReader(pdf_file)
    return "".join([p.extract_text() or "" for p in reader.pages])

def get_mermaid(text):
    match = re.search(r"```mermaid\s+(.*?)\s+```", text, re.DOTALL)
    return match.group(1) if match else None

# --- PANEL LATERAL ---
with st.sidebar:
    st.header("📂 Gestión de Archivo")
    uploaded_file = st.file_uploader("Sube tu reporte PDF", type="pdf")
    st.markdown("---")
    st.info("Al subir el archivo, se activarán las pestañas de análisis y chat.")

if uploaded_file:
    # Guardamos el texto en la sesión para que el chat no lo olvide
    if 'pdf_text' not in st.session_state:
        with st.spinner("Leyendo documento..."):
            st.session_state.pdf_text = extract_text(uploaded_file)
    
    # ORGANIZACIÓN POR PESTAÑAS
    tab_viz, tab_chat, tab_raw = st.tabs(["🚀 Herramientas Visuales", "💬 Chat de Consultoría", "📄 Texto del PDF"])

    with tab_raw:
        st.text_area("Contenido del documento", st.session_state.pdf_text[:15000], height=400)

    with tab_viz:
        st.markdown("### ¿Qué análisis necesitas hoy?")
        c1, c2, c3, c4, c5 = st.columns(5)
        
        with c1: b_res = st.button("📝 Resumen")
        with c2: b_key = st.button("📍 Key Points")
        with c3: b_ish = st.button("🐟 Ishikawa")
        with c4: b_con = st.button("🧠 M. Conceptual")
        with c5: b_men = st.button("🌐 M. Mental")

        query = ""
        contexto = st.session_state.pdf_text[:8000]

        if b_res: query = f"Haz un resumen ejecutivo de: {contexto}"
        elif b_key: query = f"Extrae los puntos clave de: {contexto}"
        elif b_ish: query = f"Genera un diagrama de Ishikawa (mermaid graph LR) sobre los problemas en: {contexto}"
        elif b_con: query = f"Crea un mapa conceptual (mermaid mindmap) de: {contexto}"
        elif b_men: query = f"Crea un mapa mental (mermaid mindmap) de: {contexto}"

        if query:
            with st.spinner("Analizando con Gemini..."):
                model = genai.GenerativeModel("gemini-1.5-flash", system_instruction=SYSTEM_PROMPT)
                resp = model.generate_content(query)
                col_text, col_map = st.columns([1, 1.2])
                with col_text:
                    st.markdown(resp.text)
                with col_map:
                    m = get_mermaid(resp.text)
                    if m: st_mermaid.st_mermaid(m, height="500px")

    with tab_chat:
        st.subheader("💬 Consulta Directa con la IA")
        st.markdown("Haz preguntas específicas sobre el contenido de tu PDF:")
        pregunta = st.text_input("Ejemplo: ¿Qué soluciones propone el texto para los costos elevados?")
        
        if pregunta:
            with st.spinner("Consultando al experto..."):
                model = genai.GenerativeModel("gemini-1.5-flash", system_instruction=SYSTEM_PROMPT)
                chat_resp = model.generate_content(f"Contexto: {st.session_state.pdf_text[:8000]}\n\nPregunta: {pregunta}")
                st.markdown(f"<div class='chat-container'>{chat_resp.text}</div>", unsafe_allow_html=True)
else:
    st.markdown("<br><h4 style='text-align: center; color: gray;'>Sube un PDF para comenzar</h4>", unsafe_allow_html=True)
