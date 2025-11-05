"""
Input validation utilities
"""

from typing import Dict, Any, List, Optional


class ValidationError(Exception):
    """Raised when validation fails"""
    pass


class RequestValidator:
    """Validates client requests"""

    REQUIRED_FIELDS = ['UUID', 'ACTION']
    VALID_ACTIONS = ['get', 'set', 'list', 'subscribe', 'listlog']

    # Fields required for each action
    ACTION_REQUIREMENTS = {
        'get': ['ID'],
        'set': ['ID'],
        'list': [],
        'subscribe': [],
        'listlog': []
    }

    # Valid data fields for CorporateData
    CORPORATE_DATA_FIELDS = [
        'cp', 'CUIT', 'domicilio', 'idreq', 'idSeq',
        'localidad', 'provincia', 'sede', 'seqID',
        'telefono', 'web'
    ]

    @classmethod
    def validate_request(cls, request_data: Dict[str, Any]) -> None:
        """
        Validates a client request

        Args:
            request_data: The request dictionary to validate

        Raises:
            ValidationError: If validation fails
        """
        # Check required fields
        for field in cls.REQUIRED_FIELDS:
            if field not in request_data:
                raise ValidationError(f"Missing required field: {field}")

        # Validate action
        action = request_data.get('ACTION', '').lower()
        if action not in cls.VALID_ACTIONS:
            raise ValidationError(
                f"Invalid action '{action}'. "
                f"Valid actions: {', '.join(cls.VALID_ACTIONS)}"
            )

        # Check action-specific requirements
        if action in cls.ACTION_REQUIREMENTS:
            for field in cls.ACTION_REQUIREMENTS[action]:
                if field not in request_data or not request_data[field]:
                    raise ValidationError(
                        f"Action '{action}' requires field: {field}"
                    )

    @classmethod
    def validate_corporate_data(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validates and filters corporate data fields

        Args:
            data: Data dictionary to validate

        Returns:
            Dictionary with only valid corporate data fields
        """
        return {
            key: value
            for key, value in data.items()
            if key in cls.CORPORATE_DATA_FIELDS
        }

    @classmethod
    def sanitize_string(cls, value: str, max_length: Optional[int] = None) -> str:
        """
        Sanitizes string input

        Args:
            value: String to sanitize
            max_length: Maximum allowed length

        Returns:
            Sanitized string
        """
        if not isinstance(value, str):
            value = str(value)

        # Strip whitespace
        value = value.strip()

        # Truncate if needed
        if max_length and len(value) > max_length:
            value = value[:max_length]

        return value
