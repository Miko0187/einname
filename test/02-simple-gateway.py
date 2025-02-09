import dotenv
import asyncio
import aiohttp
import os
import json
from enum import Enum

dotenv.load_dotenv()

class GatewayIntent(Enum):
    GUILDS = 1 << 0
    GUILD_MEMBERS = 1 << 1
    GUILD_MODERATION = 1 << 2
    GUILD_EXPRESSIONS = 1 << 3
    GUILD_INTEGRATIONS = 1 << 4
    GUILD_WEBHOOKS = 1 << 5
    GUILD_INVITES = 1 << 6
    GUILD_VOICE_STATES = 1 << 7
    GUILD_PRESENCES = 1 << 8
    GUILD_MESSAGES = 1 << 9
    GUILD_MESSAGE_REACTIONS = 1 << 10
    GUILD_MESSAGE_TYPING = 1 << 11
    DIRECT_MESSAGES = 1 << 12
    DIRECT_MESSAGE_REACTIONS = 1 << 13
    DIRECT_MESSAGE_TYPING = 1 << 14
    MESSAGE_CONTENT = 1 << 15
    GUILD_SCHEDULED_EVENTS = 1 << 16
    AUTO_MODERATION_CONFIGURATION = 1 << 20
    AUTO_MODERATION_EXECUTION = 1 << 21
    GUILD_MESSAGE_POLLS = 1 << 24
    DIRECT_MESSAGE_POLLS = 1 << 25

def get_intent_value(*intents: GatewayIntent) -> int:
    return sum(intent.value for intent in intents)

ALL_INTENTS = get_intent_value(*GatewayIntent)

DISCORD_BASE = "https://discord.com/api/v"
DISCORD_GATEWAY = "wss://gateway.discord.gg"
API_VERSION = "10"
HEADER = {
    "Authorization": f"Bot {os.getenv('token')}",
    "Content-Type": "application/json",
    "User-Agent": "Python einname/Miko0187"
}

sequence = None
heartbeat = None

async def sendIdentify(ws):
    await ws.send_json({
        "op": 2,
        "d": {
            "token": f"Bot {os.getenv('token')}",
            "properties": {
                "os": "linux",
                "browser": "einname",
                "device": "einname"
            },
            "compress": False,
            "large_threshold": 250,
            "intents": ALL_INTENTS
        }
    })

async def heartbeatLoop(ws):
    while True:
        await ws.send_json({
            "op": 1,
            "d": sequence
        })

        await asyncio.sleep(heartbeat / 1000)

async def main():
    loop = asyncio.get_event_loop()

    async with aiohttp.ClientSession() as session:
        async with session.ws_connect(DISCORD_GATEWAY, headers=HEADER) as ws:
            async for msg in ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    data: dict = msg.json()

                    print(f"{json.dumps(data, ensure_ascii=False, indent=4)}\n")

                    if data.get("s"):
                        sequence = data["s"]

                    match data["op"]:
                        # heartbeat
                        case 1:
                            await ws.send_json({
                                "op": 1,
                                "d": sequence
                            })

                        # hello
                        case 10:
                            heartbeat = data["d"]["heartbeat_interval"]
                            
                            task = loop.create_task(heartbeatLoop(ws))

                            await sendIdentify(ws)

                        # heartbeat ack
                        case 11:
                            pass

                elif msg.type == aiohttp.WSMsgType.ERROR:
                    break

asyncio.run(main())
