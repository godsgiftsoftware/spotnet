import pytest
from aiogram.types import Message
from telegram.handlers.start import start_handler

class DummyMessage:
    def __init__(self):
        self.answered = False
        self.text = None
    async def answer(self, text):
        self.answered = True
        self.text = text

@pytest.mark.asyncio
async def test_start_handler():
    msg = DummyMessage()
    await start_handler(msg)
    assert msg.answered
    assert msg.text == "Hello! This is the Margin notification bot."
