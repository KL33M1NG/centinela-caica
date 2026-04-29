import re
import logging

logger = logging.getLogger(__name__)

# Criterios de búsqueda (los tuyos)
CRITERIOS = {
    "Potencial Donante (CAICA)": r"(caica|incucai|muerte encefalica|tallo|procuracion|en mantenimiento|ablacion|posible donante)",
    "Deterioro Neurológico": r"(glasgow [3-8]|gcs [3-8]|arreactiva|midriaticas|anisocoricas|descerebracion|decorticacion|hic|pic elevada|edema cerebral)",
    "Soporte Vital / ARM": r"(arm|tet|iot|intubado|traqueo|ventilacion mec|test de apnea)",
    "Neurocrítico": r"(tec grave|hsd|hsa|hematoma subdural|stroke|e_v_c|politraum)"
}

def limpiar_diagnostico(texto_sucio: str) -> str:
    """Extrae el diagnóstico principal del texto de una evolución."""
    match = re.search(r'(?:dx|diagnóstico|diagnostico|imp\.? dx|motivo de consulta)\s*[:|-]\s*(.+)', texto_sucio, re.IGNORECASE)
    if not match:
        return "NO DETECTADO"

    dx = match.group(1).strip()

    # Palabras que indican final del diagnóstico
    palabras_corte = [
        "CONDUCTA", "PLAN", "SOLICITO", "INDICO", "TRATAMIENTO", "TTO",
        "EVOLUCION", "EXAMEN", "ESTUDIO", "LABORATORIO", "COMIENZO", "PROCEDO"
    ]

    for palabra in palabras_corte:
        partes = re.split(rf'\b{palabra}\b', dx, flags=re.IGNORECASE)
        dx = partes[0]

    dx = re.sub(r'[\t\r\n⇆]+', ' ', dx)
    dx = re.sub(r'\s\s+', ' ', dx).strip()
    return dx.upper() if len(dx) > 3 else "NO DETECTADO"

def analizar_texto(texto_completo: str):
    """
    Recibe todo el texto de las evoluciones.
    Devuelve (lista_de_hallazgos, diagnostico_extraido)
    """
    if not texto_completo:
        return [], "NO DETECTADO"

    t_low = texto_completo.lower()
    hallazgos = []
    for categoria, patron in CRITERIOS.items():
        if re.search(patron, t_low):
            hallazgos.append(categoria)

    diagnostico = limpiar_diagnostico(texto_completo)

    # Si se configuró IA, podríamos llamarla aquí (queda pendiente)
    # if USAR_IA: ...

    return list(set(hallazgos)), diagnostico