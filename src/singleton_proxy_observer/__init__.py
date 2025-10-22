"""
SingletonProxyObserver - Sistema de Gestión de Datos Corporativos

Sistema implementado con patrones Singleton, Proxy y Observer
para gestión centralizada de datos en AWS DynamoDB con notificaciones en tiempo real.
"""

__version__ = '1.0.0'
__author__ = 'UADER - FCyT - IS2'

from . import dao
from . import patterns
from . import server
from . import utils

__all__ = ['dao', 'patterns', 'server', 'utils']
