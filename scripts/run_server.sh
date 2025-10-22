#!/bin/bash
#
# Script para ejecutar el servidor con las credenciales AWS configuradas
#

# Configurar credenciales AWS (carga desde variables de entorno o .env)
# Si necesitas establecer las credenciales aquí, usa:
# export AWS_ACCESS_KEY_ID=your_access_key
# export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_REGION=us-east-1

echo "🔐 Credenciales AWS configuradas"
echo "📍 Región: $AWS_REGION"
echo ""

# Ejecutar servidor
python3 -m singleton_proxy_observer.server.main "$@"
