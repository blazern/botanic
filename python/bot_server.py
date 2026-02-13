import asyncio
import logging
import sys
from os import getenv
from pathlib import Path

from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

import illness_schedule

TOKEN = getenv("TELEGRAM_BOT_TOKEN")
ILLNESS_SCHEDULE_DIR = Path(getenv("ILLNESS_SCHEDULE_DIR")).resolve()

dp = Dispatcher()

TELEGRAM_MAX_LEN = 4096

async def _send_in_chunks(message: Message, text: str) -> None:
    """
    Telegram hard-limits message size: https://core.telegram.org/bots/api#sendmessage
    Send as multiple messages if needed.
    """
    if len(text) <= TELEGRAM_MAX_LEN:
        await message.answer(text)
        return

    # Split by lines to avoid breaking HTML entities too much.
    lines = text.splitlines(keepends=True)
    buf = ""
    for line in lines:
        if len(buf) + len(line) > TELEGRAM_MAX_LEN:
            if buf:
                await message.answer(buf)
                buf = ""
            # If a single line is huge, hard-split it.
            while len(line) > TELEGRAM_MAX_LEN:
                await message.answer(line[:TELEGRAM_MAX_LEN])
                line = line[TELEGRAM_MAX_LEN:]
        buf += line
    if buf:
        await message.answer(buf)

@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(f"Hello, {html.bold(message.from_user.full_name)}!")

@dp.message(Command("article"))
async def article_handler(message: Message) -> None:
    """
    Usage:
      /article 57
    """
    text = (message.text or "").strip()
    parts = text.split(maxsplit=1)
    if len(parts) != 2:
        await message.answer("Usage: /article <number>\nExample: /article 57")
        return

    number = parts[1].strip()

    try:
        result = illness_schedule.get_article_text(number, ILLNESS_SCHEDULE_DIR)
        reply = (
            f'{html.link("Article link", result.url)}\n'
            f"{html.quote(result.text)}"
        )
        await _send_in_chunks(message, reply)
    except ValueError as e:
        await message.answer(f"Bad request: {html.quote(str(e))}")
    except FileNotFoundError:
        await message.answer("Article not found")
    except RuntimeError as e:
        await message.answer(f"Internal error: {html.quote(str(e))}")


async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
