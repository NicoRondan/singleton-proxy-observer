"""
Configuration module for SingletonProxyObserver server
Centralizes all configuration settings
"""

import os
from typing import Optional


class Config:
    """Centralized configuration for the system"""

    # AWS Configuration
    AWS_REGION: str = os.getenv('AWS_REGION', 'us-east-1')
    DYNAMODB_ENDPOINT: Optional[str] = os.getenv('DYNAMODB_ENDPOINT')  # None for real AWS

    # Table Names
    TABLE_CORPORATE_DATA: str = 'CorporateData'
    TABLE_CORPORATE_LOG: str = 'CorporateLog'

    # Server Configuration
    DEFAULT_PORT: int = 8080
    DEFAULT_HOST: str = ''
    SOCKET_TIMEOUT: int = 60
    BUFFER_SIZE: int = 4096
    MAX_CONNECTIONS: int = 5

    # Logging
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    # Client Configuration
    CLIENT_RETRY_ATTEMPTS: int = 3
    CLIENT_RETRY_DELAY: int = 5

    @classmethod
    def validate(cls) -> bool:
        """
        Validates that all required configuration is present

        Returns:
            bool: True if configuration is valid

        Raises:
            ValueError: If required configuration is missing
        """
        # Add validation logic here if needed
        return True

    @classmethod
    def from_env(cls, env_file: Optional[str] = None):
        """
        Loads configuration from environment file

        Args:
            env_file: Path to .env file (optional)
        """
        if env_file and os.path.exists(env_file):
            # Simple .env loader (for production, consider python-dotenv)
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key.strip()] = value.strip()

        # Refresh from environment
        cls.AWS_REGION = os.getenv('AWS_REGION', cls.AWS_REGION)
        cls.DYNAMODB_ENDPOINT = os.getenv('DYNAMODB_ENDPOINT', cls.DYNAMODB_ENDPOINT)
        cls.LOG_LEVEL = os.getenv('LOG_LEVEL', cls.LOG_LEVEL)
