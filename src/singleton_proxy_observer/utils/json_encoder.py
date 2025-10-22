"""
JSON encoding utilities
Handles special types like Decimal from DynamoDB
"""

import json
from decimal import Decimal
from typing import Any


class DecimalEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles Decimal objects from DynamoDB"""

    def default(self, obj: Any) -> Any:
        """
        Override default encoding to handle Decimal types

        Args:
            obj: Object to encode

        Returns:
            Encoded object

        """
        if isinstance(obj, Decimal):
            # Convert to int if no decimal places, otherwise to float
            if obj % 1 == 0:
                return int(obj)
            else:
                return float(obj)
        return super(DecimalEncoder, self).default(obj)


def json_dumps_decimal(obj: Any, **kwargs) -> str:
    """
    Helper function to serialize JSON with Decimal support

    Args:
        obj: Object to serialize
        **kwargs: Additional arguments for json.dumps

    Returns:
        JSON string

    Example:
        >>> data = {'price': Decimal('19.99')}
        >>> json_dumps_decimal(data)
        '{"price": 19.99}'
    """
    return json.dumps(obj, cls=DecimalEncoder, **kwargs)
