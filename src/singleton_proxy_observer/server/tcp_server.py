"""
TCP Server
Handles TCP connections and client communication
"""

import socket
import threading
import logging
import sys
import json
import time

from .config import Config
from .handlers import RequestHandler
from ..utils import json_dumps_decimal


class TCPServer:
    """
    TCP Server for handling client connections

    Manages socket connections, request routing, and graceful shutdown.
    """

    def __init__(self, port: int = Config.DEFAULT_PORT, verbose: bool = False):
        """
        Initialize TCP Server

        Args:
            port: Port number to listen on
            verbose: Enable verbose logging
        """
        self.port = port
        self.verbose = verbose
        self.running = False
        self.server_socket = None
        self.request_handler = RequestHandler()
        self._setup_logging()

    def _setup_logging(self) -> None:
        """Configure logging system"""
        level = logging.DEBUG if self.verbose else logging.INFO
        logging.basicConfig(
            level=level,
            format=Config.LOG_FORMAT
        )

    def start(self) -> None:
        """
        Start the TCP server

        Binds to port, listens for connections, and handles clients in threads.

        Raises:
            OSError: If port is already in use
            Exception: For other startup errors
        """
        try:
            # Create and configure socket
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            # Bind and listen
            self.server_socket.bind((Config.DEFAULT_HOST, self.port))
            self.server_socket.listen(Config.MAX_CONNECTIONS)
            self.running = True

            self._print_startup_banner()

            logging.info(f"Server listening on port {self.port}")

            # Main accept loop
            while self.running:
                try:
                    client_socket, client_address = self.server_socket.accept()
                    print(
                        f"🔌 Nueva conexión desde "
                        f"{client_address[0]}:{client_address[1]}",
                        flush=True
                    )
                    logging.info(f"Connection from {client_address}")

                    # Handle client in separate thread
                    client_thread = threading.Thread(
                        target=self._handle_client,
                        args=(client_socket, client_address),
                        daemon=True
                    )
                    client_thread.start()

                except socket.error as e:
                    if self.running:
                        logging.error(f"Socket error: {e}")

        except OSError as e:
            if 'Address already in use' in str(e):
                logging.error(f"Port {self.port} is already in use")
                print(f"❌ Error: Puerto {self.port} ya está en uso", flush=True)
                sys.exit(1)
            else:
                raise
        except Exception as e:
            logging.error(f"Server error: {e}", exc_info=True)
            sys.exit(1)
        finally:
            self.stop()

    def _handle_client(
        self,
        client_socket: socket.socket,
        client_address: tuple
    ) -> None:
        """
        Handle a single client connection

        Args:
            client_socket: The client's socket
            client_address: The client's address (host, port)
        """
        request_data = {}

        try:
            client_socket.settimeout(Config.SOCKET_TIMEOUT)

            # Read request
            data = b''
            while True:
                chunk = client_socket.recv(Config.BUFFER_SIZE)
                if not chunk:
                    break
                data += chunk
                if b'\n' in data:
                    break

            if not data:
                logging.debug(f"No data received from {client_address}")
                return

            # Parse request
            request_str = data.decode('utf-8').strip()
            logging.debug(f"Received: {request_str}")

            try:
                request_data = json.loads(request_str)
                action = request_data.get('ACTION', 'unknown').upper()
                item_id = request_data.get('ID', 'N/A')
                print(f"   ⚡ Procesando: {action} (ID: {item_id})", flush=True)
            except json.JSONDecodeError:
                print(
                    f"   ❌ Error: JSON inválido desde {client_address[0]}",
                    flush=True
                )
                response = {'error': 'Invalid JSON format'}
            else:
                # Process request
                response = self.request_handler.handle_request(
                    request_data,
                    client_socket
                )

                if 'error' in response:
                    print(
                        f"   ⚠️  Respuesta con error: "
                        f"{response.get('error', 'unknown')}",
                        flush=True
                    )
                else:
                    print("   ✅ Respuesta enviada exitosamente", flush=True)

            # Send response (except for subscribe which keeps connection open)
            if request_data.get('ACTION', '').lower() != 'subscribe':
                response_str = json_dumps_decimal(response) + '\n'
                client_socket.sendall(response_str.encode('utf-8'))
                logging.debug(f"Sent: {response_str}")
                client_socket.close()
            else:
                # For subscribe, send confirmation and keep connection alive
                response_str = json_dumps_decimal(response) + '\n'
                client_socket.sendall(response_str.encode('utf-8'))

                # Keep connection alive for notifications
                while True:
                    time.sleep(1)

        except socket.timeout:
            logging.debug(f"Client {client_address} timeout")
        except Exception as e:
            logging.error(
                f"Error handling client {client_address}: {e}",
                exc_info=True
            )
            # Try to send error to client
            try:
                error_response = {'error': str(e)}
                response_str = json_dumps_decimal(error_response) + '\n'
                client_socket.sendall(response_str.encode('utf-8'))
            except:
                pass
        finally:
            # Close socket unless it's a subscribed observer
            try:
                action = request_data.get('ACTION', '').lower() if request_data else ''
                if action != 'subscribe':
                    client_socket.close()
            except:
                pass

    def stop(self) -> None:
        """Stop the server gracefully"""
        self.running = False

        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass

        print("\n")
        print("=" * 60)
        print("🛑 Servidor detenido")
        print("=" * 60)
        logging.info("Server stopped")

    def _print_startup_banner(self) -> None:
        """Print startup information banner"""
        print("=" * 60, flush=True)
        print(" SERVIDOR SINGLETON-PROXY-OBSERVER", flush=True)
        print("=" * 60, flush=True)
        print("✅ Servidor iniciado exitosamente", flush=True)
        print(f"📡 Escuchando en puerto: {self.port}", flush=True)
        print(
            f"🔧 Modo verbose: "
            f"{'Activado' if self.verbose else 'Desactivado'}",
            flush=True
        )
        print(f"☁️  DynamoDB región: {Config.AWS_REGION}", flush=True)
        print("=" * 60, flush=True)
        print("💡 Presione Ctrl+C para detener el servidor", flush=True)
        print("=" * 60, flush=True)
        print("", flush=True)
