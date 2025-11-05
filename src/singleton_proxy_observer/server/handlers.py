"""
Request Handler
Processes client requests and coordinates operations
"""

import logging
import uuid
import socket
from typing import Dict, Any

from ..dao import CorporateDataDAO, CorporateLogDAO
from ..patterns import ProxyDataService, ObserverManager, ClientObserver
from ..utils import RequestValidator, ValidationError


class RequestHandler:
    """
    Handles client requests

    Coordinates between DAOs, Proxy, and Observers to process client requests.
    """

    def __init__(self):
        """Initialize request handler with required components"""
        # Create a single ObserverManager instance to share between proxy and subscriptions
        self.observer_manager = ObserverManager()
        self.log_dao = CorporateLogDAO()

        # Pass the same observer_manager to the proxy
        self.proxy_service = ProxyDataService(
            dao=CorporateDataDAO(),
            observer_manager=self.observer_manager,  # Use same instance
            log_dao=self.log_dao
        )
        self.session_id = str(uuid.uuid4())

        logging.info(f"RequestHandler initialized with session {self.session_id}")

    def handle_request(
        self,
        request_data: Dict[str, Any],
        client_socket: socket.socket
    ) -> Dict[str, Any]:
        """
        Process a client request

        Args:
            request_data: The request dictionary
            client_socket: The client's socket connection

        Returns:
            Response dictionary

        Example:
            >>> handler = RequestHandler()
            >>> response = handler.handle_request(
            ...     {'UUID': 'test', 'ACTION': 'get', 'ID': 'item1'},
            ...     socket_obj
            ... )
        """
        client_uuid = request_data.get('UUID', 'unknown')
        action = request_data.get('ACTION', '').lower()
        item_id = request_data.get('ID')

        # Log the action
        self.log_dao.log_action(client_uuid, self.session_id, action, item_id)

        try:
            # Validate request
            RequestValidator.validate_request(request_data)

            # Route to appropriate handler
            if action == 'get':
                return self._handle_get(item_id)
            elif action == 'set':
                return self._handle_set(item_id, request_data)
            elif action == 'list':
                return self._handle_list()
            elif action == 'listlog':
                return self._handle_listlog(client_uuid)
            elif action == 'subscribe':
                return self._handle_subscribe(client_uuid, client_socket)
            else:
                return {'error': f'Unknown action: {action}'}

        except ValidationError as e:
            logging.warning(f"Validation error: {e}")
            return {'error': str(e)}
        except Exception as e:
            logging.error(f"Error handling request: {e}", exc_info=True)
            return {'error': f'Internal server error: {str(e)}'}

    def _handle_get(self, item_id: str) -> Dict[str, Any]:
        """
        Handle GET request

        Args:
            item_id: ID of the item to retrieve

        Returns:
            Response with item data or error
        """
        result = self.proxy_service.get_data(item_id)

        if result:
            logging.info(f"GET successful for {item_id}")
            return {'action': 'get', 'data': result}
        else:
            logging.warning(f"GET failed: item {item_id} not found")
            return {'error': f'Item {item_id} not found'}

    def _handle_set(self, item_id: str, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle SET request

        Args:
            item_id: ID of the item to set
            request_data: Full request data

        Returns:
            Response with stored data or error
        """
        # Extract and validate corporate data fields
        data = RequestValidator.validate_corporate_data(request_data)

        if not data:
            return {'error': 'No valid data fields provided'}

        result = self.proxy_service.set_data(item_id, data)

        if result:
            logging.info(f"SET successful for {item_id}")
            return {'action': 'set', 'data': result}
        else:
            logging.error(f"SET failed for {item_id}")
            return {'error': 'Failed to set data'}

    def _handle_list(self) -> Dict[str, Any]:
        """
        Handle LIST request

        Returns:
            Response with list of all items
        """
        result = self.proxy_service.list_data()
        logging.info(f"LIST successful, returned {len(result)} items")
        return {'action': 'list', 'data': result}

    def _handle_listlog(self, client_uuid: str) -> Dict[str, Any]:
        """
        Handle LISTLOG request

        Args:
            client_uuid: UUID of the client requesting logs

        Returns:
            Response with list of log entries for this client
        """
        logs = self.log_dao.get_logs_by_client(client_uuid)
        logging.info(f"LISTLOG successful for {client_uuid}, returned {len(logs)} log entries")
        return {'action': 'listlog', 'data': logs}

    def _handle_subscribe(
        self,
        client_uuid: str,
        client_socket: socket.socket
    ) -> Dict[str, Any]:
        """
        Handle SUBSCRIBE request

        Args:
            client_uuid: UUID of the subscribing client
            client_socket: The client's socket

        Returns:
            Subscription confirmation response
        """
        observer = ClientObserver(client_socket, client_uuid)
        self.observer_manager.attach(observer)

        logging.info(
            f"Client {client_uuid} subscribed "
            f"(total observers: {self.observer_manager.get_observer_count()})"
        )

        return {
            'action': 'subscribe',
            'status': 'subscribed',
            'uuid': client_uuid
        }
