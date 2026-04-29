import asyncio
import re
import logging
from playwright.async_api import async_playwright
from config import SIPROD_USER, SIPROD_PASS, SIPROD_BASE, SERVICIOS, HEADLESS
from analizador import analizar_texto
from notificador import enviar_y_registrar

logger = logging.getLogger(__name__)

async def login(page):
    """Inicia sesión en el HIS."""
    await page.goto(f"{SIPROD_BASE}/login/Home/Welcome")
    try:
        await page.click("button.auth-btn.vgs-btn")
        await page.fill('#Username', value=SIPROD_USER)
        await page.fill('#Password', value=SIPROD_PASS)
        await page.click('button[value="login"]')
        await page.wait_for_load_state("networkidle", timeout=30000)
        logger.info("Login exitoso")
    except Exception as e:
        logger.error(f"Fallo en login automatico: {e}. Intentando acceso directo...")
        await page.goto(f"{SIPROD_BASE}/PROD_MVC/InternacionAtencionMedica/Index")

async def obtener_ids_pacientes(page, servicio_id, area_id):
    """Obtiene los IDs de pacientes internados en un servicio/area."""
    await page.goto(f"{SIPROD_BASE}/PROD_MVC/InternacionAtencionMedica/Index")
    await page.select_option("#ServicioId", servicio_id)
    await page.wait_for_timeout(3000)
    await page.select_option("#AreaId", area_id)
    try:
        await page.wait_for_selector("table#grilla tbody tr", timeout=20000)
    except:
        logger.warning(f"No se pudo cargar la grilla en {servicio_id}/{area_id}")
        return []
    contenido = await page.content()
    ids = list(set(re.findall(r'ResumenPaciente/Index/(\d+)', contenido)))
    return ids

async def extraer_datos_paciente(page, id_p, zona_nombre):
    """Va al resumen y cronologico de un paciente; devuelve datos y texto."""
    try:
        await page.goto(f"{SIPROD_BASE}/PROD_MVC/ResumenPaciente/Index/{id_p}", timeout=60000)
        await page.wait_for_selector("#HeaderHc", timeout=15000)

        header_html = await page.locator("#HeaderHc").inner_html()
        nombre_match = re.search(r'<span>([^<,]+,[^<]+)</span>', header_html)
        nombre = nombre_match.group(1).strip() if nombre_match else f"ID {id_p}"
        dni_match = re.search(r'value_CodigoHC[^>]*>(\d+)-(\d+)-', header_html)
        dni = dni_match.group(2) if dni_match else "S/D"
        edad_match = re.search(r'\((\d+\s*años[^\)]*)\)', header_html)
        edad = edad_match.group(1).strip() if edad_match else "S/D"

        body_text = await page.locator("body").inner_text()
        cama_match = re.search(r'Cama\s*:\s*([^\n\r|]+)', body_text)
        cama = cama_match.group(1).strip() if cama_match else "S/D"

        datos = {
            "id_p": id_p,
            "nombre": nombre,
            "dni": dni,
            "edad": edad,
            "cama": cama,
            "servicio": zona_nombre,
            "diagnostico": "NO DETECTADO"
        }

        # Ir al cronologico
        btn = page.locator("a", has_text="Cronologico de HC")
        texto_completo = ""
        if await btn.count() > 0:
            await btn.click()
            await page.wait_for_timeout(5000)
            for frame in page.frames:
                if await frame.locator(".grupo").count() > 0:
                    entradas = await frame.locator(".texto").all_inner_texts()
                    texto_completo = " ".join(entradas)
                    break

        return datos, texto_completo

    except Exception as e:
        logger.error(f"Error extrayendo datos de {id_p}: {e}")
        return None, None

async def ejecutar_ronda():
    """Realiza una ronda completa de monitoreo."""
    logger.info("Iniciando ronda de monitoreo...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=HEADLESS)
        context = await browser.new_context()
        page = await context.new_page()

        await login(page)

        for s_id, areas, zona in SERVICIOS:
            for a_id in areas:
                try:
                    ids = await obtener_ids_pacientes(page, s_id, a_id)
                    logger.info(f"Zona {zona} (area {a_id}) -> {len(ids)} pacientes")
                    for pid in ids:
                        datos, texto = await extraer_datos_paciente(page, pid, zona)
                        if datos and texto:
                            hallazgos, dx = analizar_texto(texto)
                            datos["diagnostico"] = dx
                            if hallazgos:
                                enviar_y_registrar(datos, hallazgos, texto)
                            logger.info(f"   OK {datos['nombre']} | {dx} | Hallazgos: {len(hallazgos)}")
                except Exception as e:
                    logger.error(f"Error en sector {zona}: {e}")

        await browser.close()
    logger.info("Ronda finalizada.")
