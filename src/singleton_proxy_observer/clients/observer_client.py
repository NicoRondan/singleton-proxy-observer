"""
Observer Client
Client for subscribing to data change notifications
"""

import json
import socket
import logging
import uuid
import time
import threading
from typing import Optional, Callable
from datetime import datetime


class ObserverClient:
    """
    Observer client for receiving change notifications

    Maintains persistent connection and receives notifications when data changes.
    Features automatic reconnection on connection loss.
    """

    DEFAULT_HOST = 'localhost'
    DEFAULT_PORT = 8080
    DEFAULT_TIMEOUT = 60
    BUFFER_SIZE = 4096
    RECONNECT_INTERVAL = 30  # seconds

    def __init__(
        self,
        host: str = DEFAULT_HOST,
        port: int = DEFAULT_PORT,
        output_file: Optional[str] = None,
        verbose: bool = False,
        on_notification: Optional[Callable] = None
    ):
        """
        Initialize observer client

        Args:
            host: Server hostname
            port: Server port
            output_file: Optional file to save notifications
            verbose: Enable verbose logging
            on_notification: Optional callback function for notifications
        """
        self.host = host
        self.port = port
        self.output_file = output_file
        self.verbose = verbose
        self.on_notification = on_notification
        self.cpu_uuid = str(uuid.getnode())

        self.connected = False
        self.client_socket = None
        self.running = True

        self._setup_logging()

    def _setup_logging(self) -> None:
        """Configure logging system"""
        level = logging.DEBUG if self.verbose else logging.INFO
        logging.basicConfig(
            level=level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

    def _write_output(self, data: dict) -> None:
        """
        Write notification data to stdout and file

        Args:
            data: Notification data to write
        """
        output_json = json.dumps(data, indent=2, ensure_ascii=False)
        timestamp = datetime.now().isoformat()

        # Write to stdout
        print(f"\n[{timestamp}] Notification received:")
        print(output_json)
        print("-" * 50)

        # Write to file if specified
        if self.output_file:
            try:
                with open(self.output_file, 'a', encoding='utf-8') as f:
                    f.write(f"\n[{timestamp}]\n")
                    f.write(output_json)
                    f.write("\n" + "-" * 50 + "\n")
            except Exception as e:
                logging.error(f"Error writing to output file: {e}")

    def _connect(self) -> bool:
        """
        Establish connection to server and subscribe

        Returns:
            True if successful, False otherwise
        """
        try:
            # Create socket
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.settimeout(self.DEFAULT_TIMEOUT)

            # Connect to server
            logging.info(f"Connecting to {self.host}:{self.port}...")
            self.client_socket.connect((self.host, self.port))

            # Send subscription request
            subscribe_request = {
                'UUID': self.cpu_uuid,
                'ACTION': 'subscribe'
            }

            request_json = json.dumps(subscribe_request) + '\n'
            logging.debug(f"Sending subscription request: {request_json}")
            self.client_socket.sendall(request_json.encode('utf-8'))

            # Receive subscription confirmation
            response_data = b''
            while b'\n' not in response_data:
                chunk = self.client_socket.recv(self.BUFFER_SIZE)
                if not chunk:
                    logging.error("Server closed connection during subscription")
                    return False
                response_data += chunk

            response_str = response_data.decode('utf-8').strip()
            logging.debug(f"Subscription response: {response_str}")

            response = json.loads(response_str)

            if response.get('status') == 'subscribed':
                self.connected = True
                logging.info("✓ Subscribed successfully")
                print(f"\n✓ Suscrito exitosamente al servidor {self.host}:{self.port}")
                print(f"  UUID: {self.cpu_uuid}")
                print("  Esperando notificaciones...\n")
                return True
            else:
                logging.error(f"Subscription failed: {response}")
                return False

        except socket.timeout:
            logging.error("Connection timeout during subscription")
            return False
        except socket.error as e:
            logging.error(f"Socket error during subscription: {e}")
            return False
        except json.JSONDecodeError as e:
            logging.error(f"Invalid JSON response: {e}")
            return False
        except Exception as e:
            logging.error(f"Unexpected error during subscription: {e}", exc_info=True)
            return False

    def _disconnect(self) -> None:
        """Close connection to server"""
        self.connected = False
        if self.client_socket:
            try:
                self.client_socket.close()
            except:
                pass
            self.client_socket = None
        logging.info("Disconnected from server")

    def _receive_notifications(self) -> None:
        """
        Main loop for receiving notifications

        Runs continuously while connected, processing incoming notifications.
        """
        buffer = b''

        while self.running and self.connected:
            try:
                # Receive data
                chunk = self.client_socket.recv(self.BUFFER_SIZE)

                if not chunk:
                    logging.warning("Server closed connection")
                    self.connected = False
                    break

                buffer += chunk

                # Process complete messages (delimited by newlines)
                while b'\n' in buffer:
                    line, buffer = buffer.split(b'\n', 1)
                    if line:
                        try:
                            notification = json.loads(line.decode('utf-8'))
                            self._handle_notification(notification)
                        except json.JSONDecodeError as e:
                            logging.error(f"Invalid JSON notification: {e}")

            except socket.timeout:
                # Timeout is normal, just continue
                continue
            except socket.error as e:
                logging.error(f"Socket error while receiving: {e}")
                self.connected = False
                break
            except Exception as e:
                logging.error(f"Unexpected error while receiving: {e}", exc_info=True)
                self.connected = False
                break

    def _handle_notification(self, notification: dict) -> None:
        """
        Handle a received notification

        Args:
            notification: The notification data
        """
        logging.debug(f"Notification received: {notification}")

        # Write output
        self._write_output(notification)

        # Call custom callback if provided
        if self.on_notification:
            try:
                self.on_notification(notification)
            except Exception as e:
                logging.error(f"Error in notification callback: {e}")

    def start(self) -> None:
        """
        Start the observer client

        Connects to server and begins listening for notifications.
        Automatically reconnects if connection is lost.
        """
        print("=" * 50)
        print(" CLIENTE OBSERVADOR")
        print("=" * 50)
        print(f"Servidor: {self.host}:{self.port}")
        print(f"UUID: {self.cpu_uuid}")
        if self.output_file:
            print(f"Archivo de salida: {self.output_file}")
        print("=" * 50)

        while self.running:
            if not self.connected:
                # Try to connect
                if self._connect():
                    # Start receiving notifications
                    self._receive_notifications()

                # If disconnected and still running, wait before reconnecting
                if self.running and not self.connected:
                    logging.info(
                        f"Reconnecting in {self.RECONNECT_INTERVAL} seconds..."
                    )
                    print(
                        f"\n⚠️  Conexión perdida. "
                        f"Reconectando en {self.RECONNECT_INTERVAL} segundos..."
                    )
                    time.sleep(self.RECONNECT_INTERVAL)

    def stop(self) -> None:
        """Stop the observer client gracefully"""
        print("\n\n🛑 Deteniendo cliente observador...")
        self.running = False
        self._disconnect()
        print("👋 Cliente observador detenido")
