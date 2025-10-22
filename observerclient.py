#!/usr/bin/env python3
"""
ObserverClient - Cliente para recibir notificaciones de cambios en CorporateData
Trabajo Práctico Final Integrador - IS2

Uso:
    python observerclient.py [-s=hostname] [-p=port] [-o=output.json] [-v]

El cliente se suscribe al servidor y recibe notificaciones cada vez que
se produce una actualización (SET) en la base de datos CorporateData.
"""

import sys
import argparse
import signal
from pathlib import Path

# Agregar src al path para importar el módulo
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from singleton_proxy_observer.clients.observer_client import ObserverClient


def main():
    """Punto de entrada principal"""
    parser = argparse.ArgumentParser(
        description='Cliente Observer para notificaciones de cambios en CorporateData',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Descripción:
  Este cliente se conecta al servidor y se suscribe para recibir notificaciones
  en tiempo real cada vez que se produzca una modificación (SET) en la base de
  datos CorporateData.

  El cliente mantiene la conexión abierta y muestra cada notificación recibida.
  En caso de pérdida de conexión, reintenta automáticamente cada 30 segundos.

Ejemplos de uso:

  # Suscribirse al servidor local
  python observerclient.py

  # Suscribirse a un servidor remoto en puerto específico
  python observerclient.py -s=192.168.1.100 -p=9000

  # Guardar notificaciones en archivo además de mostrarlas
  python observerclient.py -o=notifications.json

  # Modo verbose con logs detallados
  python observerclient.py -v

  # Todas las opciones combinadas
  python observerclient.py -s=localhost -p=8080 -o=notifications.json -v

Notificaciones recibidas:
  Cada notificación tiene el formato:
  {
    "action": "update",
    "item_id": "UADER-FCyT-IS2",
    "data": {
      "id": "UADER-FCyT-IS2",
      "cp": "3260",
      "CUIT": "30-70925411-8",
      ...
    },
    "timestamp": "2024-10-22T03:45:12.123456"
  }

Cómo detener:
  Presione Ctrl+C para detener el cliente de forma segura.
        """
    )

    parser.add_argument(
        '-s', '--server',
        default='localhost',
        help='Hostname del servidor (default: localhost)'
    )

    parser.add_argument(
        '-p', '--port',
        type=int,
        default=8080,
        help='Puerto del servidor (default: 8080)'
    )

    parser.add_argument(
        '-o', '--output',
        help='Archivo para guardar las notificaciones (opcional)'
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Modo verbose - muestra logs detallados'
    )

    parser.add_argument(
        '-r', '--reconnect-interval',
        type=int,
        default=30,
        help='Intervalo de reconexión en segundos (default: 30)'
    )

    args = parser.parse_args()

    # Mostrar banner
    print("\n" + "="*70)
    print(" OBSERVER CLIENT - Sistema de Notificaciones en Tiempo Real")
    print("="*70)
    print(f" Servidor: {args.server}:{args.port}")
    if args.output:
        print(f" Archivo de salida: {args.output}")
    print(" Presione Ctrl+C para detener")
    print("="*70 + "\n")

    # Crear cliente
    client = ObserverClient(
        host=args.server,
        port=args.port,
        output_file=args.output,
        verbose=args.verbose
    )

    # Configurar intervalo de reconexión si se especificó
    if args.reconnect_interval:
        client.RECONNECT_INTERVAL = args.reconnect_interval

    # Manejador de señales para cierre limpio
    def signal_handler(sig, frame):
        print("\n\n" + "="*70)
        print(" Deteniendo cliente Observer...")
        print("="*70)
        client.stop()
        print(" ✅ Cliente detenido correctamente")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Iniciar cliente
    try:
        print("🔄 Conectando al servidor...")
        client.start()

        # El cliente corre en su propio thread, mantener el programa vivo
        print("✅ Conectado exitosamente")
        print("👂 Esperando notificaciones...\n")

        # Esperar indefinidamente (el cliente maneja todo en su thread)
        signal.pause()

    except ConnectionRefusedError:
        print(f"\n❌ Error: No se pudo conectar al servidor en {args.server}:{args.port}")
        print("   Verifique que el servidor esté ejecutándose:")
        print(f"   python singletonproxyobserver.py -p {args.port}")
        sys.exit(1)

    except KeyboardInterrupt:
        print("\n\n" + "="*70)
        print(" Deteniendo cliente Observer...")
        print("="*70)
        client.stop()
        print(" ✅ Cliente detenido correctamente")
        sys.exit(0)

    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
