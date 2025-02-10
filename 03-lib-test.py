import asyncio
import dotenv
import logging
import os
from einname import Bot, ALL_INTENTS

logging.basicConfig(level=logging.DEBUG)
dotenv.load_dotenv()

bot = Bot(os.getenv("token"), ALL_INTENTS)

asyncio.run(bot.start())
