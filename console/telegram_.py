

import asyncio
from telegram.ext import Application
import threading
import telegram


class TelegramThread(threading.Thread):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.app = Application.builder()\
            .token(
            "7442253777:AAGdNFpx7xSx9xA2Uqo65X3FFMNQlMTo9zQ")\
            .build()
        self.loop = asyncio.new_event_loop()

    def run(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()


__telegram_thread = TelegramThread(daemon=True)
__telegram_thread.start()


def send_telegram_message(chat_id: str, message: str):
    fut = asyncio.run_coroutine_threadsafe(
        __telegram_thread.app.bot.send_message(chat_id, message), __telegram_thread.loop)
    fut.result()


def send_telegram_document(chat_id, document, filename):
    fut = asyncio.run_coroutine_threadsafe(
        __telegram_thread.app.bot.send_document(chat_id, document, filename=filename), __telegram_thread.loop)
    fut.result()
