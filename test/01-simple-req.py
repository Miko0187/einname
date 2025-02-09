import dotenv
import asyncio
import aiohttp
import os

dotenv.load_dotenv()

DISCORD_BASE = "https://discord.com/api/v"
API_VERSION = "10"

async def main():
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{DISCORD_BASE}{API_VERSION}/applications/@me", headers = {
            "Authorization": f"Bot {os.getenv('token')}",
            "Content-Type": "application/json",
            "User-Agent": "Python einname/Miko0187"
        }) as response:
            print(await response.json())

asyncio.run(main())
