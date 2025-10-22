"""
Observer Pattern Implementation
Subject-Observer notification system
"""

import socket
import threading
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Any

from ..utils import json_dumps_decimal
from .singleton import SingletonABCMeta


class Subject(ABC):
    """
    Abstract Subject interface for Observer pattern

    Defines the interface for attaching, detaching, and notifying observers.
    """

    @abstractmethod
    def attach(self, observer: 'Observer') -> None:
        """Attach an observer to this subject"""
        pass

    @abstractmethod
    def detach(self, observer: 'Observer') -> None:
        """Detach an observer from this subject"""
        pass

    @abstractmethod
    def notify(self, data: Dict[str, Any]) -> None:
        """Notify all attached observers with data"""
        pass


class Observer(ABC):
    """
    Abstract Observer interface

    Defines the update interface for objects that should be notified
    of changes in a subject.
    """

    @abstractmethod
    def update(self, data: Dict[str, Any]) -> None:
        """
        Receive update from subject

        Args:
            data: The notification data
        """
        pass


class ClientObserver(Observer):
    """
    Concrete Observer representing a connected client

    Receives notifications via TCP socket connection.
    """

    def __init__(self, client_socket: socket.socket, client_uuid: str):
        """
        Initialize client observer

        Args:
            client_socket: The client's socket connection
            client_uuid: Unique identifier for the client
        """
        self.socket: socket.socket = client_socket
        self.uuid: str = client_uuid
        self.active: bool = True
        self.lock: threading.Lock = threading.Lock()

    def update(self, data: Dict[str, Any]) -> None:
        """
        Send update to the client via socket

        Args:
            data: The notification data to send
        """
        if not self.active:
            return

        try:
            with self.lock:
                message = json_dumps_decimal(data) + '\n'
                self.socket.sendall(message.encode('utf-8'))
                logging.debug(f"Sent update to observer {self.uuid}")
        except Exception as e:
            logging.error(f"Error sending update to {self.uuid}: {e}")
            self.active = False

    def disconnect(self) -> None:
        """Mark observer as inactive and close socket"""
        self.active = False
        try:
            self.socket.close()
        except:
            pass


class ObserverManager(Subject, metaclass=SingletonABCMeta):
    """
    Singleton manager for observers

    Manages all subscribed observers and handles notifications.
    Combines Singleton and Observer patterns.
    """

    def __init__(self):
        """Initialize the observer manager"""
        self._observers: List[ClientObserver] = []
        self._lock: threading.Lock = threading.Lock()
        logging.info("ObserverManager singleton created")

    def attach(self, observer: ClientObserver) -> None:
        """
        Register a new observer

        Args:
            observer: The observer to attach
        """
        with self._lock:
            self._observers.append(observer)
            logging.info(f"Attached observer {observer.uuid}")

    def detach(self, observer: ClientObserver) -> None:
        """
        Remove an observer

        Args:
            observer: The observer to detach
        """
        with self._lock:
            if observer in self._observers:
                self._observers.remove(observer)
                observer.disconnect()
                logging.info(f"Detached observer {observer.uuid}")

    def notify(self, data: Dict[str, Any]) -> None:
        """
        Notify all active observers

        Args:
            data: The data to send to all observers

        Note:
            Automatically removes inactive observers
        """
        with self._lock:
            inactive_observers = []

            for observer in self._observers:
                try:
                    observer.update(data)
                except:
                    inactive_observers.append(observer)

            # Clean up inactive observers
            for observer in inactive_observers:
                self._observers.remove(observer)
                logging.info(f"Removed inactive observer {observer.uuid}")

    def get_observer_count(self) -> int:
        """
        Get the number of active observers

        Returns:
            Number of currently attached observers
        """
        with self._lock:
            return len(self._observers)
