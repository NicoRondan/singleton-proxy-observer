"""
Proxy Pattern Implementation
Intercepts and augments data service operations
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from datetime import datetime


class DataServiceInterface(ABC):
    """
    Abstract interface for data services

    Defines the contract that both the real service and proxy must implement.
    """

    @abstractmethod
    def get_data(self, item_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve data by ID

        Args:
            item_id: The ID of the item to retrieve

        Returns:
            Dictionary containing the item data, or None if not found
        """
        pass

    @abstractmethod
    def set_data(self, item_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Store or update data

        Args:
            item_id: The ID of the item to store
            data: The data to store

        Returns:
            The stored data, or None if operation failed
        """
        pass

    @abstractmethod
    def list_data(self) -> List[Dict[str, Any]]:
        """
        List all data items

        Returns:
            List of all items
        """
        pass


class RealDataService(DataServiceInterface):
    """
    Real data service implementation

    Performs actual data operations using a DAO.
    """

    def __init__(self, dao):
        """
        Initialize real data service

        Args:
            dao: Data Access Object for database operations
        """
        self.dao = dao

    def get_data(self, item_id: str) -> Optional[Dict[str, Any]]:
        """Get data from DAO"""
        return self.dao.get(item_id)

    def set_data(self, item_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Set data via DAO"""
        return self.dao.set(item_id, data)

    def list_data(self) -> List[Dict[str, Any]]:
        """List all data from DAO"""
        return self.dao.list_all()


class ProxyDataService(DataServiceInterface):
    """
    Proxy for data service with notification capabilities

    Intercepts data operations and triggers notifications to observers
    when data changes occur.
    """

    def __init__(self, dao, observer_manager, log_dao):
        """
        Initialize proxy data service

        Args:
            dao: Data Access Object for data operations
            observer_manager: Manager for notifying observers
            log_dao: DAO for logging operations
        """
        self._real_service = RealDataService(dao)
        self._observer_manager = observer_manager
        self._log_dao = log_dao

    def get_data(self, item_id: str) -> Optional[Dict[str, Any]]:
        """
        Proxy for get operation

        Simply forwards to real service (no interception needed for reads).

        Args:
            item_id: The ID to retrieve

        Returns:
            The retrieved data
        """
        logging.debug(f"Proxy: GET operation for {item_id}")
        return self._real_service.get_data(item_id)

    def set_data(self, item_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Proxy for set operation with notification

        Intercepts the SET operation to:
        1. Execute the real operation
        2. Notify all observers of the change

        Args:
            item_id: The ID to set
            data: The data to store

        Returns:
            The stored data
        """
        logging.debug(f"Proxy: SET operation for {item_id}")

        # Execute real operation
        result = self._real_service.set_data(item_id, data)

        # Intercept and notify observers if successful
        if result:
            notification = {
                'action': 'update',
                'item_id': item_id,
                'data': result,
                'timestamp': datetime.utcnow().isoformat()
            }
            self._observer_manager.notify(notification)
            logging.info(f"Proxy: Notified observers of change to {item_id}")

        return result

    def list_data(self) -> List[Dict[str, Any]]:
        """
        Proxy for list operation

        Simply forwards to real service (no interception needed for reads).

        Returns:
            List of all data
        """
        logging.debug("Proxy: LIST operation")
        return self._real_service.list_data()
