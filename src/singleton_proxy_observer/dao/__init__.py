"""
Data Access Objects (DAOs)
Handles database operations for DynamoDB tables
"""

from .base import DynamoDBConnection
from .corporate_data import CorporateDataDAO
from .corporate_log import CorporateLogDAO

__all__ = [
    'DynamoDBConnection',
    'CorporateDataDAO',
    'CorporateLogDAO',
]
