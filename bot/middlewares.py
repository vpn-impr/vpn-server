import time
from collections.abc import Awaitable, Callable
from typing import Any, cast
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Update
import logging

HANDLED_STR = ["Unhandled", "Handled"]

class RemoveInlineReplayMarkup(BaseMiddleware):
    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        super().__init__()

    async def __call__(
        self,
        handler: Callable[[Update, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        event = cast(Update, event)
        _started_processing_at = time.time()
        if event.callback_query:
            await event.callback_query.message.edit_reply_markup(reply_markup=None)
        await handler(event, data)
        return