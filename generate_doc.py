import os
import sys
from docx import Document
from docx.shared import Inches, Pt, Mm
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from datetime import datetime

LOGO_PATH = os.path.join("assets", "logo_mgi.png")

def add_page_break(doc):
    doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)

def add_header_with_logo(doc):
    if not os.path.exists(LOGO_PATH):
        print("⚠️ Logo no encontrado")
        return False
    for section in doc.sections:
        header = section.header
        paragraph = header.paragraphs[0] if header.paragraphs else header.add_paragraph()
        paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
        run = paragraph.add_run()
        run.add_picture(LOGO_PATH, width=Inches(1.5))
    return True

def get_bing_captures(bing_dir):
    """Agrupa las capturas Bing por idioma y categoría."""
    capturas = {"es": {}, "en": {}}
    for fname in os.listdir(bing_dir):
        if not fname.endswith(".png"):
            continue
        parts = fname.split("_", 2)
        if len(parts) < 3:
            continue
        lang, categoria, _ = parts
        if lang in capturas:
            capturas[lang].setdefault(categoria.replace("_", " "), []).append(os.path.join(bing_dir, fname))
    return capturas

def create_word_doc(nombre, ofac_dir, bing_dir, output_path):
    doc = Document()
    doc.styles['Normal'].font.name = 'Calibri'
    doc.styles['Normal'].font.size = Pt(11)

    for section in doc.sections:
        section.top_margin = Mm(20)
        section.bottom_margin = Mm(20)
        section.left_margin = Mm(25)
        section.right_margin = Mm(25)

    add_header_with_logo(doc)

    now = datetime.now()
    doc.add_heading("Informe de Debida Diligencia", level=0).alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph("Este informe contiene capturas de pantalla de:")
    doc.add_paragraph("• Lista de sanciones OFAC")
    doc.add_paragraph("• Búsquedas temáticas en Bing (español e inglés)")
    doc.add_paragraph(f"Fecha: {now.strftime('%d/%m/%Y')} — Hora: {now.strftime('%H:%M')}")

    add_page_break(doc)
    doc.add_heading(nombre, level=1)

    # === OFAC SECTION ===
    doc.add_heading("Búsqueda en lista OFAC", level=2)
    ofac_imgs = [f for f in os.listdir(ofac_dir) if f.endswith(".png")]
    if ofac_imgs:
        img_path = os.path.join(ofac_dir, ofac_imgs[0])
        doc.add_picture(img_path, width=Inches(5.0))
    else:
        doc.add_paragraph("❌ No se encontró captura de OFAC.")
    add_page_break(doc)

    # === BING SECTION ===
    doc.add_heading("Búsquedas en Bing por categoría de riesgo", level=2)
    capturas = get_bing_captures(bing_dir)

    for lang in ["es", "en"]:
        doc.add_heading("Español" if lang == "es" else "English", level=3)
        for categoria, paths in capturas[lang].items():
            doc.add_heading(f"Categoría: {categoria}", level=4)
            doc.add_paragraph("Términos buscados:", style='List Bullet')
            doc.add_paragraph("Ver criterios predefinidos en el sistema.")  # puedes personalizar esto
            for path in paths:
                if os.path.exists(path):
                    para = doc.add_paragraph()
                    para.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    para.add_run().add_picture(path, width=Inches(4.75))
                else:
                    doc.add_paragraph("❌ Imagen no disponible.")
            add_page_break(doc)

    doc.save(output_path)
    print(f"✅ Documento generado: {output_path}")
    return output_path

# === USO DIRECTO DESDE TERMINAL ===
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("⚠️ Debes proporcionar un nombre como argumento.")
        sys.exit(1)

    nombre = sys.argv[1]
    nombre_safe = nombre.replace(" ", "_")
    carpeta_base = os.path.join("capturas", nombre_safe)
    ofac_dir = os.path.join(carpeta_base, "ofac")
    bing_dir = os.path.join(carpeta_base, "bing")
    output_file = f"Informe_Debida_Diligencia_{nombre_safe}.docx"

    create_word_doc(nombre, ofac_dir, bing_dir, output_file)
