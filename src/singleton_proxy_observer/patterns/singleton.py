"""
Singleton Pattern Implementation
Thread-safe singleton metaclass
"""

import threading
from abc import ABC
from typing import Dict, Any


class SingletonMeta(type):
    """
    Thread-safe Singleton metaclass

    This metaclass ensures that only one instance of a class exists
    across the entire application, even in multi-threaded environments.

    Example:
        >>> class MyClass(metaclass=SingletonMeta):
        ...     pass
        >>> obj1 = MyClass()
        >>> obj2 = MyClass()
        >>> obj1 is obj2
        True
    """

    _instances: Dict[type, Any] = {}
    _lock: threading.RLock = threading.RLock()  # RLock allows re-entrance from same thread

    def __call__(cls, *args, **kwargs):
        """
        Controls instance creation

        Returns:
            The singleton instance of the class
        """
        if cls not in cls._instances:
            with cls._lock:
                # Double-checked locking pattern
                if cls not in cls._instances:
                    instance = super().__call__(*args, **kwargs)
                    cls._instances[cls] = instance
        return cls._instances[cls]


class SingletonABCMeta(SingletonMeta, type(ABC)):
    """
    Combined metaclass for classes that need both Singleton and ABC

    This allows a class to be both a Singleton and have abstract methods.

    Example:
        >>> class MyAbstractSingleton(ABC, metaclass=SingletonABCMeta):
        ...     @abstractmethod
        ...     def my_method(self):
        ...         pass
    """
    pass
