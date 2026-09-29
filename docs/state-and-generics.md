# State-dependent APIs

[Project overview and reading path](../README.md)

An email draft has text but no recipient. Sending it before choosing a recipient
is a mistake the caller should discover while writing code.

**Typical Python**

```python,ignore
class Email:
    def __init__(self, body: str) -> None:
        self.body = body
        self.recipient: str | None = None

    def send(self, deliver: Callable[[str, str], None]) -> None:
        if self.recipient is None:
            raise ValueError("recipient required")
        deliver(self.recipient, self.body)


Email("Hello").send(record_delivery)
```

The checker accepts `send` because the method exists on every `Email`. The
missing recipient is discovered only when this call runs.

**Alternative**

```python,ignore
@dataclass(frozen=True)
class DraftEmail:
    body: str

    def to(self, recipient: str) -> "AddressedEmail":
        return AddressedEmail(recipient, self.body)


@dataclass(frozen=True)
class AddressedEmail:
    recipient: str
    body: str

    def send(self, deliver: Callable[[str, str], None]) -> None:
        deliver(self.recipient, self.body)


DraftEmail("Hello").to("reader@example.com").send(record_delivery)
```

[Source](../examples/email_state.py)

`DraftEmail("Hello").send(record_delivery)` is now rejected as
`missing-attribute`. Calling `.to("reader@example.com")` returns an
`AddressedEmail`, which can be sent. The in-memory delivery function records
`("reader@example.com", "Hello")`.

The type distinction ensures a recipient field is present; it does not validate
the address or prove delivery succeeds. Validate an external address at the
boundary and use a [typed outcome](errors-and-absence.md) for delivery failures
the caller can handle. The original draft remains usable after `.to()`; Python
does not enforce Rust-style moves.
