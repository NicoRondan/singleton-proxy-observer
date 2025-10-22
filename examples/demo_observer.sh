#!/bin/bash
#
# Demo del ObserverClient
# Muestra cómo suscribirse y recibir notificaciones en tiempo real
#

echo "============================================================"
echo " DEMO: Observer Client - Notificaciones en Tiempo Real"
echo "============================================================"
echo ""
echo "Este demo muestra el patrón Observer en acción:"
echo "1. El cliente se suscribe al servidor"
echo "2. Espera notificaciones de cambios"
echo "3. Cada vez que otro cliente hace SET, recibe una notificación"
echo ""
echo "Para ver el Observer en acción:"
echo "  Terminal 1: python observerclient.py -v"
echo "  Terminal 2: python singletonclient.py -i=examples/input_set.json"
echo ""
echo "============================================================"
echo "Iniciando Observer Client..."
echo "============================================================"
echo ""

# Ejecutar observer client
python3 observerclient.py -o=observer_notifications.json -v
