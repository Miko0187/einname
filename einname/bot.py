import asyncio
from .intents import GatewayIntent, ALL_INTENTS, get_intent_value
from .gateway import Gateway

class Bot:
    def __init__(self, token: str, intents: list[GatewayIntent] = []):
        self.token = token
        self.intents = get_intent_value(intents) if type(intents) != int else intents

        self.id: int | None
        self.username: str | None
        self.discriminator: str | None
        self.guilds: any | None

        self._loop = asyncio.get_event_loop()
        self._gateway = Gateway(self.token, self.intents, self._loop)

    async def start(self):
        await self._gateway._connect()  
    