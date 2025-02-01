from ..model.models import OrderStatus, PaymentMethod, UserType
from decimal import Decimal

"""Convert an OrderStatus enum value to its name."""
def get_order_status_name(status_value):
    return OrderStatus(status_value).name if status_value in OrderStatus._value2member_map_ else "Unknown"

"""Convert a PaymentMethod enum value to its name."""
def get_order_payment_method_name(status_value):
    return PaymentMethod(status_value).name if status_value in PaymentMethod._value2member_map_ else "Unknown"

"""Convert a UserType enum value to its name."""
def get_user_type_name(type_value):
    return UserType(type_value).name if type_value in UserType._value2member_map_ else "Unknown"

def decimal(value):
    try:
        return Decimal(value).quantize(Decimal('0.01'))
    except (ValueError, TypeError):
        return value