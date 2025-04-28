import os
import sys
import asyncio
import random
from playwright.async_api import async_playwright
import nest_asyncio

nest_asyncio.apply()

# === CRITERIOS DEFINIDOS POR EL USUARIO (NO TOCAR) ===
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

async def take_ofac_screenshot(name, page, folder):
    await page.goto("https://sanctionssearch.ofac.treas.gov/")
    await page.fill("#ctl00_MainContent_txtLastName", name)
    await page.click("#ctl00_MainContent_btnSearch")
    await page.wait_for_timeout(3000)

    path = os.path.join(folder, f"ofac_{name.replace(' ', '_')}.png")
    await page.screenshot(path=path, clip={"x": 0, "y": 0, "width": 1200, "height": 1050})
    has_results = await page.query_selector("#gvSearchResults") is not None

    return {"type": "OFAC", "name": name, "path": path, "has_results": has_results}

async def take_bing_screenshot(name, query, category, page, folder, lang="es"):
    query_str = f'"{name}" AND {query}'
    url = f"https://www.bing.com/search?q={query_str}&count=10"
    await page.goto(url)
    await page.wait_for_load_state("networkidle")
    await page.wait_for_timeout(random.randint(2000, 3000))

    filename = f"{lang}_{category.replace(' ', '_')}_{name.replace(' ', '_')}.png"
    path = os.path.join(folder, filename)
    element = await page.query_selector('#b_results')

    try:
        if element:
            await element.screenshot(path=path)
        else:
            await page.screenshot(path=path, full_page=True)
    except:
        path = None

    return {"type": "Bing", "name": name, "category": category, "criterios": query, "lang": lang, "path": path}

async def run_searches(name, ofac_dir, bing_dir):
    results = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1600, "height": 1200})
        page = await context.new_page()

        results.append(await take_ofac_screenshot(name, page, ofac_dir))

        for cat, expr in criterios_es.items():
            results.append(await take_bing_screenshot(name, expr, cat, page, bing_dir, lang="es"))

        for cat, expr in criterios_en.items():
            results.append(await take_bing_screenshot(name, expr, cat, page, bing_dir, lang="en"))

        await browser.close()
    return results

# === EJECUCIÓN DESDE TERMINAL ===
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("⚠️ Debes proporcionar un nombre como argumento.")
        sys.exit(1)

    nombre = sys.argv[1]
    nombre_safe = nombre.replace(" ", "_")
    output_dir = os.path.join("capturas", nombre_safe)
    ofac_dir = os.path.join(output_dir, "ofac")
    bing_dir = os.path.join(output_dir, "bing")
    os.makedirs(ofac_dir, exist_ok=True)
    os.makedirs(bing_dir, exist_ok=True)

    asyncio.run(run_searches(nombre, ofac_dir, bing_dir))
