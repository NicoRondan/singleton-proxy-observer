"""
Design Patterns Implementation
Singleton, Proxy, and Observer patterns
"""

from .singleton import SingletonMeta, SingletonABCMeta
from .observer import Observer, Subject, ClientObserver, ObserverManager
from .proxy import DataServiceInterface, RealDataService, ProxyDataService

__all__ = [
    # Singleton
    'SingletonMeta',
    'SingletonABCMeta',
    # Observer
    'Observer',
    'Subject',
    'ClientObserver',
    'ObserverManager',
    # Proxy
    'DataServiceInterface',
    'RealDataService',
    'ProxyDataService',
]
