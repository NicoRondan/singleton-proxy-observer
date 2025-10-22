"""
Corporate Data DAO
Handles access to CorporateData table in DynamoDB
"""

import logging
from typing import Optional, Dict, List, Any
from botocore.exceptions import ClientError

from ..patterns import SingletonMeta
from .base import DynamoDBConnection


class CorporateDataDAO(metaclass=SingletonMeta):
    """
    Singleton DAO for CorporateData table

    Provides CRUD operations for corporate data.
    """

    def __init__(self):
        """Initialize Corporate Data DAO"""
        from ..server.config import Config

        self.connection = DynamoDBConnection()
        self.table = self.connection.get_table(Config.TABLE_CORPORATE_DATA)
        logging.info("CorporateDataDAO singleton created")

    def get(self, item_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve an item by ID

        Args:
            item_id: The ID of the item to retrieve

        Returns:
            Dictionary with item data, or None if not found

        Example:
            >>> dao = CorporateDataDAO()
            >>> data = dao.get('UADER-FCyT-IS2')
        """
        try:
            response = self.table.get_item(Key={'id': item_id})
            item = response.get('Item')

            if item:
                logging.debug(f"Retrieved item {item_id} from CorporateData")
            else:
                logging.debug(f"Item {item_id} not found in CorporateData")

            return item
        except ClientError as e:
            logging.error(f"Error getting item {item_id}: {e}")
            return None
        except Exception as e:
            logging.error(f"Unexpected error getting item {item_id}: {e}")
            return None

    def set(self, item_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Create or update an item

        Args:
            item_id: The ID of the item
            data: Dictionary with item data

        Returns:
            The stored data, or None if operation failed

        Example:
            >>> dao = CorporateDataDAO()
            >>> result = dao.set('UADER-FCyT-IS2', {
            ...     'cp': '3260',
            ...     'CUIT': '30-70925411-8'
            ... })
        """
        try:
            # Ensure ID is in the data
            data['id'] = item_id

            self.table.put_item(Item=data)
            logging.info(f"Stored item {item_id} in CorporateData")

            return data
        except ClientError as e:
            logging.error(f"Error setting item {item_id}: {e}")
            return None
        except Exception as e:
            logging.error(f"Unexpected error setting item {item_id}: {e}")
            return None

    def list_all(self) -> List[Dict[str, Any]]:
        """
        List all items in the table

        Returns:
            List of all items

        Note:
            This performs a scan operation which can be expensive for large tables

        Example:
            >>> dao = CorporateDataDAO()
            >>> all_items = dao.list_all()
        """
        try:
            response = self.table.scan()
            items = response.get('Items', [])

            logging.debug(f"Retrieved {len(items)} items from CorporateData")

            return items
        except ClientError as e:
            logging.error(f"Error listing items: {e}")
            return []
        except Exception as e:
            logging.error(f"Unexpected error listing items: {e}")
            return []

    def delete(self, item_id: str) -> bool:
        """
        Delete an item

        Args:
            item_id: The ID of the item to delete

        Returns:
            True if successful, False otherwise

        Example:
            >>> dao = CorporateDataDAO()
            >>> success = dao.delete('UADER-FCyT-IS2')
        """
        try:
            self.table.delete_item(Key={'id': item_id})
            logging.info(f"Deleted item {item_id} from CorporateData")
            return True
        except ClientError as e:
            logging.error(f"Error deleting item {item_id}: {e}")
            return False
        except Exception as e:
            logging.error(f"Unexpected error deleting item {item_id}: {e}")
            return False
