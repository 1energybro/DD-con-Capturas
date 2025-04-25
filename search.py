import os
import asyncio
import random
from datetime import datetime
from playwright.async_api import async_playwright
import nest_asyncio

nest_asyncio.apply()

# Carpeta de capturas
OFAC_DIR = "screenshots/ofac"
BING_DIR = "screenshots/bing"
os.makedirs(OFAC_DIR, exist_ok=True)
os.makedirs(BING_DIR, exist_ok=True)

# Categorías y términos (resumido aquí, puedes expandir en utils.py si lo prefieres)
criterios = [
    ["corrupción", "soborno", "cohecho"],
    ["fraude", "lavado de dinero", "evasión de impuestos"],
    ["crimen organizado", "narcotráfico", "cártel"],
    ["sancionado", "penalización", "regulador"],
    ["derechos humanos", "trabajo forzado", "discriminación"],
    ["terrorismo", "OFAC", "lista negra"],
    ["demandado", "litigio", "queja"],
    ["bancarrota", "quiebra", "insolvencia"],
    ["investigación criminal", "fiscalía", "testigo protegido"],
    ["gobierno", "funcionario", "congreso"]
]

categorias = [
    "Corrupción", "Delitos financieros", "Delitos penales", "Sanciones y regulación",
    "Derechos humanos y condiciones laborales", "Terrorismo y financiamiento ilícito",
    "Litigios y problemas legales", "Insolvencia y problemas financieros",
    "Justicia penal y cooperación", "Riesgo político y conexiones gubernamentales"
]

async def take_ofac_screenshot(name, page):
    await page.goto("https://sanctionssearch.ofac.treas.gov/")
    await page.fill("#ctl00_MainContent_txtLastName", name)
    await page.click("#ctl00_MainContent_btnSearch")
    await page.wait_for_timeout(3000)

    path = os.path.join(OFAC_DIR, f"ofac_{name.replace(' ', '_')}.png")
    await page.screenshot(path=path, clip={"x": 0, "y": 0, "width": 1200, "height": 1050})
    has_results = await page.query_selector("#gvSearchResults") is not None

    return {
        "type": "OFAC",
        "name": name,
        "path": path,
        "has_results": has_results
    }

async def take_bing_screenshot(name, criterios_categoria, category, page):
    criterios_str = " OR ".join(f'"{term}"' for term in criterios_categoria)
    query = f'"{name}" ({criterios_str})'
    url = f"https://www.bing.com/search?q={query}&count=10"
    
    await page.goto(url)
    await page.wait_for_load_state("networkidle")
    await page.wait_for_timeout(random.randint(2000, 3000))

    results_element = await page.query_selector('#b_results')
    path = os.path.join(BING_DIR, f"bing_{category.replace(' ', '_')}_{name.replace(' ', '_')}.png")

    try:
        if results_element:
            await results_element.screenshot(path=path)
        else:
            await page.screenshot(path=path, full_page=True)
    except:
        path = None

    return {
        "type": "Bing",
        "name": name,
        "category": category,
        "criterios": criterios_categoria,
        "path": path
    }

async def _run_searches(name):
    results = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1600, "height": 1200})
        page = await context.new_page()

        results.append(await take_ofac_screenshot(name, page))

        for criterios_categoria, categoria in zip(criterios, categorias):
            r = await take_bing_screenshot(name, criterios_categoria, categoria, page)
            results.append(r)

        await browser.close()
    return results

def run_searches(name):
    return asyncio.run(_run_searches(name))
