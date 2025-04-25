import streamlit as st
import subprocess
import os
import shutil
from datetime import datetime

st.set_page_config(page_title="Generador DD con Capturas", layout="wide")

# Logo
from PIL import Image
logo = Image.open("assets/logo_mgi.png")
st.columns([6, 1])[0].image(logo, width=300)
st.columns([6, 1])[1].markdown("<p style='text-align: right;'>¿Dudas o sugerencias? <a href='mailto:hugo.cervantes@grupomexgas.com'>Contáctanos</a></p>", unsafe_allow_html=True)

st.title("📄 Generador de Reporte de Debida Diligencia con Capturas")

# Acceso
email = st.text_input("Introduce tu correo corporativo para continuar:")

if email.endswith("@grupomexgas.com"):
    st.success(f"Acceso concedido para: {email}")

    nombre = st.text_input("Introduce el nombre de la persona o empresa a investigar:")

    if nombre:
        st.markdown(f"🕵️ Generando reporte para: **{nombre}**")
        
        # Guardar el nombre en archivo temporal para que lo usen los scripts
        with open("nombre_actual.txt", "w", encoding="utf-8") as f:
            f.write(nombre)

        # Botón para ejecutar búsqueda y generación
        if st.button("🔍 Ejecutar búsqueda y generar reporte"):
            with st.spinner("Ejecutando búsqueda en OFAC y Bing..."):
                subprocess.run(["python", "search.py", nombre], check=True)
            
            with st.spinner("Generando documento Word..."):
                subprocess.run(["python", "generate_doc.py", nombre], check=True)

            st.success("✅ Reporte generado correctamente.")

            # Buscar el documento generado
            files = [f for f in os.listdir() if f.startswith("Informe_Debida_Diligencia") and f.endswith(".docx")]
            if files:
                file_path = files[-1]
                with open(file_path, "rb") as f:
                    st.download_button(
                        label="📥 Descargar reporte",
                        data=f,
                        file_name=file_path,
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )
else:
    if email:
        st.error("Acceso denegado. Usa tu correo @grupomexgas.com para continuar.")
