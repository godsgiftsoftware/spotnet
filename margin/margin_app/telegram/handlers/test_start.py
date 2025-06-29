
"""Tests for the start handler of the Telegram bot."""
import pytest
from aiogram.types import Message
from telegram.handlers.start import start_handler

class DummyMessage:
    """A dummy message class for testing the handler."""
    def __init__(self):
        self.answered = False
        self.text = None
    async def answer(self, text):
        """Mock answer method to simulate bot reply."""
        self.answered = True
        self.text = text

@pytest.mark.asyncio
async def test_start_handler():
    """Test that the start handler sends the correct welcome message."""
    msg = DummyMessage()
    await start_handler(msg)
    assert msg.answered
    assert msg.text == "Hello! This is the Margin notification bot."
