"""Expose sending only after a draft acquires a recipient."""

from collections.abc import Callable
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class DraftEmail:
    """Hold message text without offering a send operation."""

    body: str

    def to(self, recipient: str) -> "AddressedEmail":
        """Return a message whose recipient is explicit in its type."""
        return AddressedEmail(recipient, self.body)


@dataclass(frozen=True, slots=True)
class AddressedEmail:
    """Expose sending for a message with a recipient field."""

    recipient: str
    body: str

    def send(self, deliver: Callable[[str, str], None]) -> None:
        """Pass the addressed message to the supplied delivery function."""
        deliver(self.recipient, self.body)


outbox: list[tuple[str, str]] = []


def record_delivery(recipient: str, body: str) -> None:
    """Record a delivery without external I/O."""
    outbox.append((recipient, body))


draft = DraftEmail("Hello")
addressed = draft.to("reader@example.com")
addressed.send(record_delivery)
# rejected[missing-attribute]: draft.send(record_delivery)
