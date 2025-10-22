"""
Base DAO and DynamoDB Connection
Provides singleton connection to AWS DynamoDB
"""

import logging
import boto3
from typing import Optional

from ..patterns import SingletonMeta


class DynamoDBConnection(metaclass=SingletonMeta):
    """
    Singleton connection to DynamoDB

    Ensures only one connection instance exists across the application.
    """

    def __init__(self):
        """Initialize DynamoDB connection"""
        self.dynamodb = None
        self._connect()
        logging.info("DynamoDB connection singleton created")

    def _connect(self) -> None:
        """
        Establish connection to DynamoDB

        Raises:
            Exception: If connection fails
        """
        from ..server.config import Config

        try:
            if Config.DYNAMODB_ENDPOINT:
                # Local DynamoDB
                self.dynamodb = boto3.resource(
                    'dynamodb',
                    region_name=Config.AWS_REGION,
                    endpoint_url=Config.DYNAMODB_ENDPOINT
                )
                logging.info(f"Connected to local DynamoDB at {Config.DYNAMODB_ENDPOINT}")
            else:
                # AWS DynamoDB
                self.dynamodb = boto3.resource(
                    'dynamodb',
                    region_name=Config.AWS_REGION
                )
                logging.info(f"Connected to AWS DynamoDB in region {Config.AWS_REGION}")
        except Exception as e:
            logging.error(f"Error connecting to DynamoDB: {e}")
            raise

    def get_table(self, table_name: str):
        """
        Get reference to a DynamoDB table

        Args:
            table_name: Name of the table

        Returns:
            Table resource

        Example:
            >>> conn = DynamoDBConnection()
            >>> table = conn.get_table('MyTable')
        """
        return self.dynamodb.Table(table_name)

    def reconnect(self) -> None:
        """Force reconnection to DynamoDB"""
        self._connect()
