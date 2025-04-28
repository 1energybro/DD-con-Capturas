import streamlit as st
import urllib.parse
from PIL import Image
from datetime import datetime
import csv

st.set_page_config(page_title="Buscador de DD", layout="wide")

# Cargar logo
logo = Image.open("logo_mgi.png")
st.columns([6, 1])[0].image(logo, width=300)
st.columns([6, 1])[1].markdown("<p style='text-align: right;'>¿Dudas o sugerencias? <a href='mailto:hugo.cervantes@grupomexgas.com'>Contáctanos</a></p>", unsafe_allow_html=True)

# Introducción explicativa
st.title("🔎 Generador de Búsquedas de Debida Diligencia")
st.markdown("""
El presente programa fue elaborado por la **Gerencia de Planeación Estratégica** y la **Gerencia de Compliance** de **Mex Gas Internacional**.

Su propósito es facilitar la verificación digital de antecedentes públicos sobre personas físicas y morales mediante términos de búsqueda estructurados en **10 categorías temáticas**.

El presente ejercicio identifica **112 términos** seleccionados por su frecuencia de aparición en litigios, sanciones, investigaciones periodísticas y regulatorias.

La aplicación genera enlaces de búsqueda en **Google** y **Bing**, que permiten consultar fuentes públicas rápidamente con criterios homogéneos y auditables.
""")

# Función para registrar logs
def log_busqueda(usuario, nombre_buscado):
    with open('log_busquedas.csv', 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([datetime.now(), usuario, nombre_buscado])

email = st.text_input("Introduce tu correo de Mex Gas y continúa presionando Enter:")

if email.endswith("@grupomexgas.com"):
    st.success(f"Acceso concedido para: {email}")

    # Crear 3 columnas de 5 nombres cada una
    col1, col2, col3 = st.columns(3)
    nombres = []

    with col1:
        st.subheader("Nombres (1-5)")
        for i in range(1, 6):
            nombre = st.text_input(f"Nombre {i}", key=f"nombre_{i}")
            if nombre:
                nombres.append(nombre)

    with col2:
        st.subheader("Nombres (6-10)")
        for i in range(6, 11):
            nombre = st.text_input(f"Nombre {i}", key=f"nombre_{i}")
            if nombre:
                nombres.append(nombre)

    with col3:
        st.subheader("Nombres (11-15)")
        for i in range(11, 16):
            nombre = st.text_input(f"Nombre {i}", key=f"nombre_{i}")
            if nombre:
                nombres.append(nombre)

    if nombres:
        criterios_es = {
            "Corrupción": "(\"corrupción\" OR \"soborno\" OR \"cohecho\" OR \"DOF\" OR \"SEC\" OR \"escándalo\" OR \"mordida\" OR \"comisión ilegal\" OR \"pago indebido\")",
            "Delitos financieros": "(\"fraude\" OR \"lavado de dinero\" OR \"evasión de impuestos\" OR \"paraíso fiscal\" OR \"información privilegiada\" OR \"manipulación\" OR \"falsificación\" OR \"malversación\" OR \"desfalco\" OR \"estafa\" OR \"blanqueo de capitales\" OR \"facturero\")",
            "Delitos penales": "(\"actividades ilegales\" OR \"crimen organizado\" OR \"narcotráfico\" OR \"drogas\" OR \"delito\" OR \"cártel\" OR \"tráfico\" OR \"criminal\" OR \"procesado\" OR \"acusado\" OR \"condenado\" OR \"crimen de guerra\" OR \"huachicol\")",
            "Sanciones y regulación": "(\"sancionado\" OR \"sancionada\" OR \"penalización\" OR \"suspendido\" OR \"multa\" OR \"inhabilitación\" OR \"advertencia\" OR \"regulador\" OR \"irregular\" OR \"irregularidad\" OR \"incumplimiento\" OR \"violación regulatoria\")",
            "Derechos humanos y condiciones laborales": "(\"derechos humanos\" OR \"violación de derechos\" OR \"esclavitud\" OR \"trabajo forzado\" OR \"explotación\" OR \"condiciones inhumanas\" OR \"condiciones insalubres\" OR \"violación ambiental\" OR \"discriminación\" OR \"acoso\" OR \"abuso\")",
            "Terrorismo y financiamiento ilícito": "(\"terrorismo\" OR \"financiamiento del terrorismo\" OR \"extremismo\" OR \"grupo terrorista\" OR \"radicalización\" OR \"financiamiento ilícito\" OR \"sanción internacional\" OR \"lista negra\" OR \"lista de vigilancia\" OR \"OFAC\")",
            "Litigios y problemas legales": "(\"demanda judicial\" OR \"demandado\" OR \"litigio\" OR \"pleito legal\" OR \"impugnar\" OR \"apelar\" OR \"queja\" OR \"citación\" OR \"infracción de patentes\" OR \"infracción de propiedad intelectual\" OR \"disputa\" OR \"conflicto legal\")",
            "Insolvencia y problemas financieros": "(\"bancarrota\" OR \"insolvencia\" OR \"insolvente\" OR \"quiebra\" OR \"suspensión de pagos\" OR \"reestructuración\" OR \"dificultades financieras\" OR \"coacción financiera\" OR \"embargo\" OR \"liquidación\" OR \"concurso de acreedores\")",
            "Justicia penal y cooperación": "(\"investigación criminal\" OR \"policía federal\" OR \"fiscalía\" OR \"proceso penal\" OR \"negociación de la condena\" OR \"acuerdo de clemencia\" OR \"testigo protegido\" OR \"colaboración eficaz\" OR \"delación premiada\")",
            "Riesgo político y conexiones gubernamentales": "(\"político\" OR \"gobierno\" OR \"servicio público\" OR \"funcionario\" OR \"cargo público\" OR \"partido político\" OR \"congreso\" OR \"senado\" OR \"legislador\" OR \"donación política\" OR \"vínculo político\" OR \"conflicto de interés\")"
        }

        criterios_en = {
            "Corruption": "(\"corruption\" OR \"bribery\" OR \"kickback\" OR \"DOF\" OR \"SEC\" OR \"scandal\" OR \"grease payment\" OR \"illegal commission\" OR \"undue payment\")",
            "Financial Crimes": "(\"fraud\" OR \"money laundering\" OR \"tax evasion\" OR \"tax haven\" OR \"insider trading\" OR \"manipulation\" OR \"forgery\" OR \"embezzlement\" OR \"misappropriation\" OR \"scam\" OR \"capital washing\" OR \"shell company\")",
            "Criminal Offenses": "(\"illegal activities\" OR \"organized crime\" OR \"drug trafficking\" OR \"drugs\" OR \"crime\" OR \"cartel\" OR \"trafficking\" OR \"criminal\" OR \"indicted\" OR \"accused\" OR \"convicted\" OR \"war crime\" OR \"fuel theft\")",
            "Sanctions and Regulation": "(\"sanctioned\" OR \"penalty\" OR \"suspended\" OR \"fine\" OR \"disqualification\" OR \"warning\" OR \"regulator\" OR \"irregular\" OR \"irregularity\" OR \"non-compliance\" OR \"regulatory violation\")",
            "Human Rights and Labor Conditions": "(\"human rights\" OR \"rights violation\" OR \"slavery\" OR \"forced labor\" OR \"exploitation\" OR \"inhumane conditions\" OR \"unsanitary conditions\" OR \"environmental violation\" OR \"discrimination\" OR \"harassment\" OR \"abuse\")",
            "Terrorism and Illicit Financing": "(\"terrorism\" OR \"terrorist financing\" OR \"extremism\" OR \"terrorist group\" OR \"radicalization\" OR \"illicit financing\" OR \"international sanction\" OR \"blacklist\" OR \"watchlist\" OR \"OFAC\")",
            "Lawsuits and Legal Issues": "(\"lawsuit\" OR \"defendant\" OR \"litigation\" OR \"legal dispute\" OR \"challenge\" OR \"appeal\" OR \"complaint\" OR \"summons\" OR \"patent infringement\" OR \"IP infringement\" OR \"dispute\" OR \"legal conflict\")",
            "Insolvency and Financial Problems": "(\"bankruptcy\" OR \"insolvency\" OR \"insolvent\" OR \"collapse\" OR \"payment suspension\" OR \"restructuring\" OR \"financial distress\" OR \"financial coercion\" OR \"seizure\" OR \"liquidation\" OR \"creditors' meeting\")",
            "Criminal Justice and Cooperation": "(\"criminal investigation\" OR \"federal police\" OR \"prosecutor\" OR \"criminal proceedings\" OR \"plea bargain\" OR \"leniency agreement\" OR \"protected witness\" OR \"effective collaboration\" OR \"whistleblower\")",
            "Political Risk and Government Ties": "(\"political\" OR \"government\" OR \"public service\" OR \"official\" OR \"public office\" OR \"political party\" OR \"congress\" OR \"senate\" OR \"legislator\" OR \"political donation\" OR \"political ties\" OR \"conflict of interest\")"
        }

        for nombre in nombres:
            col1, col2 = st.columns(2, gap="large")
        
            with col1:
                st.markdown(f"### Enlaces en Español para **{nombre}**")
                for categoria, expresion in criterios_es.items():
                    cadena_busqueda = f'"{nombre}" AND {expresion}'
                    url_google = f"https://www.google.com/search?q={urllib.parse.quote(cadena_busqueda)}"
                    url_bing = f"https://www.bing.com/search?q={urllib.parse.quote(cadena_busqueda)}"
                    st.markdown(f"**{categoria}**")
                    st.markdown(f"- [Buscar en Google]({url_google})")
                    st.markdown(f"- [Buscar en Bing]({url_bing})")
        
            with col2:
                st.markdown(f"### Links in English for **{nombre}**")
                for categoria, expresion in criterios_en.items():
                    cadena_busqueda = f'"{nombre}" AND {expresion}'
                    url_google = f"https://www.google.com/search?q={urllib.parse.quote(cadena_busqueda)}"
                    url_bing = f"https://www.bing.com/search?q={urllib.parse.quote(cadena_busqueda)}"
                    st.markdown(f"**{categoria}**")
                    st.markdown(f"- [Search on Google]({url_google})")
                    st.markdown(f"- [Search on Bing]({url_bing})")
        
            # Barra divisoria personalizada en color guinda
            st.markdown(
                "<hr style='border: 2px solid #800000; margin-top: 50px; margin-bottom: 50px;'>",
                unsafe_allow_html=True
            )
else:
    if email:
        st.error("Acceso denegado: usa un correo @grupomexgas.com")
