import streamlit as st
import subprocess
import os
from PIL import Image
from datetime import datetime

st.set_page_config(page_title="Buscador DD con Capturas", layout="wide")

# Logo y contacto
logo = Image.open("assets/logo_mgi.png")
st.columns([6, 1])[0].image(logo, width=300)
st.columns([6, 1])[1].markdown(
    "<p style='text-align: right;'>¿Dudas o sugerencias? "
    "<a href='mailto:hugo.cervantes@grupomexgas.com'>Contáctanos</a></p>",
    unsafe_allow_html=True
)

st.title("📄 Generador de Reporte de Debida Diligencia con Capturas")

# Validación de correo corporativo
email = st.text_input("Introduce tu correo corporativo para continuar:")

if email.endswith("@grupomexgas.com"):
    st.success(f"Acceso concedido para: {email}")

    nombre = st.text_input("Introduce el nombre de la persona o empresa a investigar:")

    if nombre:
        st.markdown(f"🕵️ Generando reporte para: **{nombre}**")

        if st.button("🔍 Ejecutar búsqueda y generar reporte"):
            with st.spinner("Ejecutando búsqueda en OFAC y Bing..."):
                result1 = subprocess.run(["python", "search.py", nombre], capture_output=True, text=True)
                st.text(result1.stdout or result1.stderr)

            with st.spinner("Generando documento Word..."):
                result2 = subprocess.run(["python", "generate_doc.py", nombre], capture_output=True, text=True)
                st.text(result2.stdout or result2.stderr)

            nombre_safe = nombre.replace(" ", "_")
            doc_name = f"Informe_Debida_Diligencia_{nombre_safe}.docx"
            if os.path.exists(doc_name):
                with open(doc_name, "rb") as file:
                    st.download_button(
                        label="📥 Descargar reporte Word",
                        data=file,
                        file_name=doc_name,
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )
            else:
                st.error("❌ No se generó el documento correctamente.")
else:
    if email:
        st.error("Acceso denegado. Usa tu correo @grupomexgas.com para continuar.")
