"""
Server Main Entry Point
Starts the SingletonProxyObserver TCP server
"""

import argparse
import logging
import socket
import sys
from pathlib import Path
from dotenv import load_dotenv

from .config import Config
from .tcp_server import TCPServer

# Auto-load environment variables from config/.env
# This ensures AWS credentials are always loaded automatically
env_path = Path(__file__).parent.parent.parent.parent / 'config' / '.env'
if env_path.exists():
    load_dotenv(env_path)
    logging.debug(f"Loaded environment variables from {env_path}")


def check_port_available(port: int) -> bool:
    """
    Check if a port is available

    Args:
        port: Port number to check

    Returns:
        True if port is available, False otherwise
    """
    test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        test_socket.bind(('', port))
        test_socket.close()
        return True
    except OSError:
        return False


def main():
    """Main entry point for the server"""
    parser = argparse.ArgumentParser(
        description='SingletonProxyObserver TCP Server',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                    # Start with default port 8080
  %(prog)s -p 9000            # Start on port 9000
  %(prog)s -v                 # Start with verbose logging
  %(prog)s -p 9000 -v         # Custom port with verbose logging
        """
    )
    parser.add_argument(
        '-p', '--port',
        type=int,
        default=Config.DEFAULT_PORT,
        help=f'Port to listen on (default: {Config.DEFAULT_PORT})'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose (DEBUG) logging'
    )
    parser.add_argument(
        '--env-file',
        type=str,
        help='Path to .env file for configuration'
    )

    args = parser.parse_args()

    # Load configuration from env file if provided
    if args.env_file:
        Config.from_env(args.env_file)

    # Verify port is available
    print(f"⚙️  Verificando disponibilidad del puerto {args.port}...", flush=True)

    if not check_port_available(args.port):
        print(f"❌ Error: Puerto {args.port} ya está en uso", flush=True)
        print("\nPosibles soluciones:", flush=True)
        print("  1. Cerrar la aplicación que está usando el puerto", flush=True)
        print("  2. Usar un puerto diferente con: -p <puerto>", flush=True)
        sys.exit(1)

    # Initialize server
    print("⚙️  Inicializando servidor y conectando a DynamoDB...", flush=True)
    server = TCPServer(port=args.port, verbose=args.verbose)

    # Start server
    try:
        server.start()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupción recibida...", flush=True)
        logging.info("Server interrupted by user")
        server.stop()
        print("👋 Adiós!", flush=True)
        sys.exit(0)
    except Exception as e:
        logging.error(f"Fatal error: {e}", exc_info=True)
        print(f"\n❌ Error fatal: {e}", flush=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
