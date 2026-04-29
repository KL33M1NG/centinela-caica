import requests
import logging
from config import NTFY_TOPIC, NTFY_TOKEN
from modelos import SessionLocal, Alerta
import datetime

logger = logging.getLogger(__name__)

def ya_notificado_hoy(paciente_id: str) -> bool:
    """Evita enviar múltiples alertas para el mismo paciente en el día."""
    db = SessionLocal()
    hoy = datetime.date.today()
    existe = db.query(Alerta).filter(
        Alerta.paciente_id == paciente_id,
        Alerta.fecha_hora >= hoy
    ).first()
    db.close()
    return existe is not None

def enviar_y_registrar(datos: dict, hallazgos: list, texto_cronologico: str):
    """
    datos: diccionario con id_p, nombre, dni, edad, servicio, cama, diagnostico
    hallazgos: lista de strings
    """
    if not hallazgos:
        return

    # Evitar duplicados hoy
    if ya_notificado_hoy(datos['id_p']):
        logger.info(f"Paciente {datos['nombre']} ya fue notificado hoy.")
        return

    hallazgos_str = ", ".join(hallazgos)

    # Preparar mensaje para ntfy
    mensaje = (
        f"🚩 ALERTA CENTINELA\n"
        f"👤 {datos['nombre']}\n"
        f"🆔 DNI: {datos['dni']}\n"
        f"🎂 Edad: {datos['edad']}\n"
        f"📍 {datos['servicio']} - Cama: {datos['cama']}\n"
        f"📋 Dx: {datos['diagnostico']}\n"
        f"🔍 Hallazgos: {hallazgos_str}"
    )

    headers = {
        "Title": "CAICA",
        "Priority": "urgent",
        "Tags": "hospital,warning"
    }
    if NTFY_TOKEN:
        headers["Authorization"] = f"Bearer {NTFY_TOKEN}"

    enviado = False
    try:
        resp = requests.post(
            f"https://ntfy.sh/{NTFY_TOPIC}",
            data=mensaje.encode('utf-8'),
            headers=headers,
            timeout=15
        )
        enviado = resp.status_code == 200
    except Exception as e:
        logger.error(f"Error al enviar notificación: {e}")

    # Registrar en base de datos
    db = SessionLocal()
    alerta = Alerta(
        paciente_id=datos['id_p'],
        nombre=datos['nombre'],
        dni=datos['dni'],
        edad=datos['edad'],
        servicio=datos['servicio'],
        cama=datos['cama'],
        diagnostico=datos['diagnostico'],
        hallazgos=hallazgos_str,
        texto_cronologico=texto_cronologico,
        enviado=enviado
    )
    db.add(alerta)
    db.commit()
    db.close()

    if enviado:
        logger.info(f"✅ Alerta enviada: {datos['nombre']}")
    else:
        logger.warning(f"❌ No se pudo enviar la alerta de {datos['nombre']} (quedó registrada igual)")