import asyncio
import aiohttp
import logging
import sys
from .events import Events
from .user import User

DISCORD_GATEWAY = "wss://gateway.discord.gg/?v=10&encoding=json"
logger = logging.getLogger(__name__)

class Gateway:
    def __init__(
        self, 
        token: str, 
        intents: int, 
        loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
    ):
        self._token = token
        self._intents = intents

        self._sequence: int = None
        self._heartbeat: int
        self._resume_gateway: str
        self._session_id: str

        self._loop: asyncio.AbstractEventLoop = loop
        self._session: aiohttp.ClientSession
        self._ws: aiohttp.ClientWebSocketResponse
        self._heartbeat_loop_task: asyncio.Task

        self._user: User
        self._guilds: any # TODO: Add guilds

    async def _send_heartbeat(self):
        logger.debug("Sending heartbeat")

        await self._ws.send_json({
            "op": 1,
            "d": self._sequence
        })

    async def _heartbeat_loop(self):
        logger.debug("Started Heartbeat loop")

        while True:
            await self._send_heartbeat()

            await asyncio.sleep(self._heartbeat / 1000)

    # TODO: Add reconnecting
    async def _connect(self):
        logger.debug("Connecting to Discord gateway")

        self._session = aiohttp.ClientSession()
        self._ws = await self._session.ws_connect(DISCORD_GATEWAY)

        while True:
            msg: aiohttp.WSMessage = await self._ws.receive()

            match msg.type:
                case aiohttp.WSMsgType.TEXT:
                    data: dict = msg.json()

                    if data.get("s"):
                        self._sequence = data["s"]

                    await self._handle_data(data)

                case aiohttp.WSMsgType.ERROR:
                    logger.fatal("Received error")
                    
                    break

    async def _login(self):
        logger.debug("Logging into gateway")

        await self._ws.send_json({
            "op": 2,
            "d": {
                "token": f"Bot {self._token}",
                "properties": {
                    "os": sys.platform,
                    "browser": "einname",
                    "device": "einname"
                },
                "compress": False, # TODO: Change this
                "intents": self._intents
            }
        })

    async def _handle_data(self, data: dict):
        match data["op"]:
            case 0:
                logger.debug(f"[0] Received {data['t']} event")

                await self._handle_event(data)

            case 1:
                logger.debug("[1] Received Heartbeat request")

                await self._send_heartbeat()
            
            case 10:
                logger.debug("[10] Received Hello")

                self._heartbeat = data["d"]["heartbeat_interval"]
                self._heartbeat_loop_task = asyncio.create_task(self._heartbeat_loop())

                await self._login()

            case 11:
                logger.debug("[11] Discord Heartbeat ACK")

                # TODO: check for too long no opcode 11
                # https://discord.com/developers/docs/events/gateway#connection-lifecycle

    # https://discord.com/developers/docs/events/gateway-events#receive-events
    async def _handle_event(self, data: dict):
        match data["t"]:
            case Events.Ready:
                self._user = User(
                    id=data["d"]["id"],
                    global_name=data["d"].get("global_name"),
                    username=data["d"]["username"],
                    bot=data["d"]["bot"],
                    avatar=data["d"].get("avatar"),
                    discriminator=data["d"]["discriminator"],
                    mfa_enabled=data["d"].get("mfa_enabled", False),
                    verified=data["d"].get("verified", False)
                )
