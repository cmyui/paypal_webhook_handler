import logging
from typing import Any
from typing import Awaitable
from typing import Callable
from typing import Mapping
from typing import TypeVar

EventHandler = TypeVar(
    "EventHandler",
    bound=Callable[[Mapping[str, Any]], Awaitable[None]],
)

_handlers = {}


def register(event: str):
    def inner(f: EventHandler) -> EventHandler:
        _handlers[event] = f
        return f
    return inner


async def handle(data: Mapping[str, Any]) -> None:
    event_type = data["event_type"]

    if handler := _handlers.get(event_type):
        await handler(data)

        logging.info(f"Handled event: {event_type}")
    else:
        logging.warning(f"Unhandled event: {event_type}")


@register("CHECKOUT.ORDER.COMPLETED")
async def checkout_order_completed(data: Mapping[str, Any]) -> None:
    ...
