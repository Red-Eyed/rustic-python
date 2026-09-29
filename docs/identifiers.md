# Distinct identifiers

[Project overview and reading path](../README.md)

An order service passes customer IDs and order IDs between helpers. Both are integers, so swapping them can produce a plausible but incorrect reference.

**Typical Python**

```python,ignore
def order_reference(customer_id: int, order_id: int) -> str:
    return f"customer:{customer_id}/order:{order_id}"


customer_id, order_id = 7, 42
reference = order_reference(order_id, customer_id)
```

The checker accepts this call. It produces `"customer:42/order:7"` instead of `"customer:7/order:42"`.

**Alternative**

```python,ignore
CustomerId = NewType("CustomerId", int)
OrderId = NewType("OrderId", int)


def order_reference(customer_id: CustomerId, order_id: OrderId) -> str:
    return f"customer:{customer_id}/order:{order_id}"
```

[Source](../examples/semantic_types.py)

The valid call produces `"customer:7/order:42"`. The swapped call and plain
integer arguments are rejected as `bad-argument-type`. `NewType` preserves which
kind of identifier the caller holds without wrapping the runtime integer.

Constructing `CustomerId(42)` cannot prove that 42 identifies a customer, or that
an order belongs to them. Establish those facts at the input or database boundary.
Use distinct types where they survive through an API; keep numerical arrays and
tensors in their framework's native types.
