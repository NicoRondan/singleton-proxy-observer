"""
Corporate Log DAO
Handles logging of all operations to CorporateLog table
"""

import logging
import uuid
from datetime import datetime
from typing import Optional
from botocore.exceptions import ClientError

from ..patterns import SingletonMeta
from .base import DynamoDBConnection


class CorporateLogDAO(metaclass=SingletonMeta):
    """
    Singleton DAO for CorporateLog table

    Provides audit logging for all system operations.
    """

    def __init__(self):
        """Initialize Corporate Log DAO"""
        from ..server.config import Config

        self.connection = DynamoDBConnection()
        self.table = self.connection.get_table(Config.TABLE_CORPORATE_LOG)
        logging.info("CorporateLogDAO singleton created")

    def log_action(
        self,
        uuid_client: str,
        session_id: str,
        action: str,
        item_id: Optional[str] = None,
        details: Optional[dict] = None
    ) -> bool:
        """
        Log an action to the audit log

        Args:
            uuid_client: UUID of the client performing the action
            session_id: Session identifier
            action: The action being performed (GET, SET, LIST, etc.)
            item_id: ID of the item being acted upon (optional)
            details: Additional details about the action (optional)

        Returns:
            True if logging successful, False otherwise

        Example:
            >>> log_dao = CorporateLogDAO()
            >>> log_dao.log_action(
            ...     uuid_client='client-123',
            ...     session_id='session-456',
            ...     action='SET',
            ...     item_id='UADER-FCyT-IS2'
            ... )
        """
        try:
            log_entry = {
                'id': str(uuid.uuid4()),
                'uuid': uuid_client,
                'session': session_id,
                'action': action.upper(),
                'timestamp': datetime.utcnow().isoformat()
            }

            if item_id:
                log_entry['item_id'] = item_id

            if details:
                log_entry['details'] = details

            self.table.put_item(Item=log_entry)
            logging.debug(f"Logged action: {action} by {uuid_client}")

            return True
        except ClientError as e:
            logging.error(f"Error logging action: {e}")
            return False
        except Exception as e:
            logging.error(f"Unexpected error logging action: {e}")
            return False

    def get_logs_by_client(self, uuid_client: str, limit: int = 100):
        """
        Retrieve logs for a specific client

        Args:
            uuid_client: The client UUID
            limit: Maximum number of logs to retrieve (0 = no limit)

        Returns:
            List of log entries

        Note:
            This uses scan which is not efficient for large tables.
            For production, create a GSI on 'uuid' field.
        """
        try:
            items = []
            scan_kwargs = {
                'FilterExpression': '#uuid = :uuid',
                'ExpressionAttributeNames': {'#uuid': 'uuid'},
                'ExpressionAttributeValues': {':uuid': uuid_client}
            }

            # Paginate through all results
            while True:
                response = self.table.scan(**scan_kwargs)
                items.extend(response.get('Items', []))

                # Check if we have enough items or if there are more pages
                if limit > 0 and len(items) >= limit:
                    return items[:limit]

                # Check if there are more pages
                if 'LastEvaluatedKey' not in response:
                    break

                scan_kwargs['ExclusiveStartKey'] = response['LastEvaluatedKey']

            return items
        except ClientError as e:
            logging.error(f"Error retrieving logs for {uuid_client}: {e}")
            return []
