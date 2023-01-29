import json

from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.types import CallbackQuery


class CallMiddle(BaseMiddleware):

    async def on_process_callback_query(self, callback: CallbackQuery, data: dict):
        # data = {'hj': 12}  # json.loads(callback.data)
        pass
