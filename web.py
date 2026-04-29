import sys
import io
import threading
import asyncio
import logging
from flask import Flask, render_template, jsonify, request
from modelos import SessionLocal, Alerta
from scraper import ejecutar_ronda
from config import SERVICIOS

# Corregir encoding para Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Configurar logging general
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("centinela.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)

app = Flask(__name__)

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/api/alertas')
def api_alertas():
    db = SessionLocal()
    alertas = db.query(Alerta).order_by(Alerta.fecha_hora.desc()).limit(100).all()
    db.close()
    resultado = []
    for a in alertas:
        resultado.append({
            "fecha": a.fecha_hora.strftime("%d/%m/%Y %H:%M"),
            "nombre": a.nombre,
            "dni": a.dni,
            "edad": a.edad,
            "servicio": a.servicio,
            "cama": a.cama,
            "diagnostico": a.diagnostico,
            "hallazgos": a.hallazgos,
            "enviado": a.enviado
        })
    return jsonify(resultado)

@app.route('/api/estado')
def api_estado():
    """Devuelve datos simples para saber si el sistema esta vivo."""
    return jsonify({
        "status": "activo",
        "servicios": len(SERVICIOS),
        "ultima_ronda": "ver log"
    })

@app.route('/api/escanear', methods=['POST'])
def forzar_escanear():
    """Ejecuta una ronda manual ahora."""
    threading.Thread(target=lambda: asyncio.run(ejecutar_ronda())).start()
    return jsonify({"mensaje": "Escaneo manual iniciado"})

if __name__ == '__main__':
    from tareas import iniciar_programador
    iniciar_programador()
    app.run(host='0.0.0.0', port=5000, debug=False)
