#!/usr/bin/env python3
"""
SingletonProxyObserver - Servidor de aplicaciones con patrones de diseño
Trabajo Práctico Final Integrador - IS2

Este servidor implementa:
- Patrón Singleton: Para gestión de conexiones a DynamoDB
- Patrón Proxy: Para interceptar operaciones y agregar funcionalidad
- Patrón Observer: Para notificar cambios a clientes suscritos

Uso:
    python singletonproxyobserver.py [-p=port] [-v]
"""

import sys
from pathlib import Path

# Agregar src al path para importar el módulo
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from singleton_proxy_observer.server.main import main

if __name__ == '__main__':
    main()
