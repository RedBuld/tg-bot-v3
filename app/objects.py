import os
import redis.asyncio as redis
from aiogram import Bot
from aiogram import Dispatcher
from aiogram.client.telegram import TelegramAPIServer
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.fsm.storage.redis import RedisStorage, DefaultKeyBuilder
from app.classes.database import DataBase
from app.configs import GC

DB = DataBase()

RD = redis.Redis.from_url( GC.redis_server, protocol=3, decode_responses=True )

if os.environ.get('LOCAL_SERVER'):
    local_server = TelegramAPIServer.from_base( GC.local_server, is_local=True )
    session = AiohttpSession( api=local_server )
    BOT = Bot(os.environ.get("BOT_TOKEN"), session=session)
else:
    BOT = Bot(os.environ.get("BOT_TOKEN"))

kb = DefaultKeyBuilder(prefix='fsm', with_bot_id=True, with_destiny=True)
storage = RedisStorage( RD, key_builder=kb )
DP = Dispatcher(storage=storage)