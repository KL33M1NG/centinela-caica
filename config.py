import os
from dotenv import load_dotenv

load_dotenv()

# Credenciales
SIPROD_USER = os.getenv("SIPROD_USERNAME")
SIPROD_PASS = os.getenv("SIPROD_PASSWORD")
SIPROD_BASE = os.getenv("SIPROD_BASE_URL", "https://his.catamarca.gob.ar")

# Notificaciones
NTFY_TOPIC = os.getenv("NTFY_TOPIC")
NTFY_TOKEN = os.getenv("NTFY_TOKEN")

# IA (opcional)
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
USAR_IA = bool(OPENAI_KEY)

# Headless para Playwright (True en producción, False si querés ver el navegador)
HEADLESS = True

# Servicios y áreas a monitorear (igual que en tu script original)
SERVICIOS = [
    ("69", ["106"], "UTI I"),
    ("99", ["138"], "UTI II"),
    ("88", ["113"], "UCO"),
    ("67", ["110"], "Emergencias"),
    ("101", ["140"], "Quemados"),
    ("23", ["39", "123", "134", "124", "125"], "Cirugia Gral"),
    ("100", ["142", "141"], "Cx Oncologica"),
    ("24", ["108", "117"], "Clinica Medica"),
    ("45", ["29"], "Traumatologia"),
    ("89", ["114", "115", "24"], "Oncologia"),
    ("94", ["126"], "Salud Mental")
]