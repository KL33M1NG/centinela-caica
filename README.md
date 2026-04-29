@"
# Centinela CAICA 🏥

Sistema autónomo de monitoreo de potenciales donantes de órganos para el hospital.
Escanea servicios de internación, analiza evoluciones médicas y envía alertas en tiempo real.

## Características
- Dashboard web para ver alertas en tiempo real
- Escaneo automático cada 15 minutos
- Detección de criterios neurológicos y de donación
- Notificaciones vía ntfy.sh
- Historial persistente en SQLite

## Instalación
pip install -r requirements.txt
playwright install chromium

## Configuración
1. Copiar .env.example a .env
2. Completar con credenciales reales
3. Ejecutar: python web.py
"@ | Out-File -FilePath README.md -Encoding UTF8

git add README.md
git commit -m "Agrego README con instrucciones"
git push
