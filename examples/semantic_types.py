"""Reject swapped identifiers even when both are stored as integers."""

from typing import NewType

CustomerId = NewType("CustomerId", int)
OrderId = NewType("OrderId", int)


def order_reference(customer_id: CustomerId, order_id: OrderId) -> str:
    """Format an order reference without checking existence or ownership."""
    return f"customer:{customer_id}/order:{order_id}"


customer_id = CustomerId(7)
order_id = OrderId(42)
reference = order_reference(customer_id, order_id)
# rejected[bad-argument-type]: order_reference(order_id, customer_id)
# rejected[bad-argument-type]: order_reference(7, 42)
