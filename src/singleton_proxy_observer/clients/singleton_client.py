"""
Singleton Client
Client for CRUD operations on CorporateData via TCP/JSON
"""

import json
import socket
import logging
import uuid
from typing import Dict, Optional, Any


class SingletonClient:
    """
    Client for interacting with the SingletonProxyObserver server

    Supports GET, SET, and LIST operations via TCP/JSON protocol.
    """

    DEFAULT_HOST = 'localhost'
    DEFAULT_PORT = 8080
    DEFAULT_TIMEOUT = 30
    BUFFER_SIZE = 4096

    def __init__(
        self,
        host: str = DEFAULT_HOST,
        port: int = DEFAULT_PORT,
        verbose: bool = False,
        timeout: int = DEFAULT_TIMEOUT
    ):
        """
        Initialize the client

        Args:
            host: Server hostname
            port: Server port
            verbose: Enable verbose logging
            timeout: Socket timeout in seconds
        """
        self.host = host
        self.port = port
        self.verbose = verbose
        self.timeout = timeout
        self.cpu_uuid = str(uuid.getnode())  # Unique CPU-based UUID
        self._setup_logging()

    def _setup_logging(self) -> None:
        """Configure logging system"""
        level = logging.DEBUG if self.verbose else logging.WARNING
        logging.basicConfig(
            level=level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

    def _send_request(self, request_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Send a request to the server and receive response

        Args:
            request_data: Request data dictionary

        Returns:
            Response dictionary or None on error
        """
        client_socket = None

        try:
            # Create TCP socket
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.settimeout(self.timeout)

            # Connect to server
            logging.debug(f"Connecting to {self.host}:{self.port}")
            client_socket.connect((self.host, self.port))

            # Add CPU UUID to request
            request_data['UUID'] = self.cpu_uuid

            # Send request
            request_json = json.dumps(request_data) + '\n'
            logging.debug(f"Sending: {request_json}")
            client_socket.sendall(request_json.encode('utf-8'))

            # Receive response
            response_data = b''
            while True:
                chunk = client_socket.recv(self.BUFFER_SIZE)
                if not chunk:
                    break
                response_data += chunk
                if b'\n' in response_data:
                    break

            # Parse response
            if response_data:
                response_str = response_data.decode('utf-8').strip()
                logging.debug(f"Received: {response_str}")
                return json.loads(response_str)
            else:
                logging.error("Empty response from server")
                return {'error': 'Empty response from server'}

        except socket.timeout:
            logging.error("Connection timeout")
            return {'error': 'Connection timeout'}
        except socket.error as e:
            logging.error(f"Socket error: {e}")
            return {'error': f'Connection error: {e}'}
        except json.JSONDecodeError as e:
            logging.error(f"JSON decode error: {e}")
            return {'error': f'Invalid JSON response: {e}'}
        except Exception as e:
            logging.error(f"Unexpected error: {e}", exc_info=True)
            return {'error': f'Unexpected error: {e}'}
        finally:
            if client_socket:
                try:
                    client_socket.close()
                except:
                    pass

    def get(self, item_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve an item by ID

        Args:
            item_id: The ID of the item to retrieve

        Returns:
            Item data dictionary or None if not found

        Example:
            >>> client = SingletonClient()
            >>> data = client.get('UADER-FCyT-IS2')
        """
        request = {
            'ACTION': 'get',
            'ID': item_id
        }

        response = self._send_request(request)

        if response and 'error' not in response:
            return response.get('data')
        else:
            error_msg = response.get('error', 'Unknown error') if response else 'No response'
            logging.error(f"GET failed: {error_msg}")
            return None

    def set(self, item_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Create or update an item

        Args:
            item_id: The ID of the item
            data: Dictionary with item data

        Returns:
            Stored data dictionary or None if failed

        Example:
            >>> client = SingletonClient()
            >>> result = client.set('UADER-FCyT-IS2', {
            ...     'cp': '3260',
            ...     'CUIT': '30-70925411-8'
            ... })
        """
        request = {
            'ACTION': 'set',
            'ID': item_id,
            **data  # Spread data fields into request
        }

        response = self._send_request(request)

        if response and 'error' not in response:
            return response.get('data')
        else:
            error_msg = response.get('error', 'Unknown error') if response else 'No response'
            logging.error(f"SET failed: {error_msg}")
            return None

    def list_all(self) -> Optional[list]:
        """
        List all items

        Returns:
            List of all items or None if failed

        Example:
            >>> client = SingletonClient()
            >>> all_items = client.list_all()
        """
        request = {
            'ACTION': 'list'
        }

        response = self._send_request(request)

        if response and 'error' not in response:
            return response.get('data', [])
        else:
            error_msg = response.get('error', 'Unknown error') if response else 'No response'
            logging.error(f"LIST failed: {error_msg}")
            return None

    def execute_from_file(
        self,
        input_file: str,
        output_file: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Execute request from JSON file

        Args:
            input_file: Path to input JSON file
            output_file: Optional path to output JSON file

        Returns:
            Response dictionary or None on error
        """
        try:
            # Read input file
            with open(input_file, 'r') as f:
                request_data = json.load(f)

            # Send request
            response = self._send_request(request_data)

            # Write output file if specified
            if output_file and response:
                with open(output_file, 'w') as f:
                    json.dump(response, f, indent=2)

            return response

        except FileNotFoundError:
            logging.error(f"Input file not found: {input_file}")
            return {'error': f'Input file not found: {input_file}'}
        except json.JSONDecodeError as e:
            logging.error(f"Invalid JSON in input file: {e}")
            return {'error': f'Invalid JSON in input file: {e}'}
        except Exception as e:
            logging.error(f"Error executing from file: {e}", exc_info=True)
            return {'error': f'Error executing from file: {e}'}
