from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from scraper import ejecutar_ronda
import logging
import asyncio

logger = logging.getLogger(__name__)
scheduler = BackgroundScheduler()

def wrapper_ejecutar_ronda():
    """Wrapper para ejecutar la ronda asíncrona desde un job síncrono."""
    try:
        asyncio.run(ejecutar_ronda())
    except Exception as e:
        logger.error(f"Error en la ronda programada: {e}")

def iniciar_programador():
    scheduler.add_job(
        wrapper_ejecutar_ronda,
        IntervalTrigger(minutes=15),
        id='ronda_principal',
        replace_existing=True
    )
    scheduler.start()
    logger.info("Programador de rondas iniciado (cada 15 min).")