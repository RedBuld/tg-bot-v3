import os
import redis.asyncio as redis
from aiogram import Bot
from aiogram import Dispatcher
from aiogram.client.telegram import TelegramAPIServer
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.fsm.storage.redis import RedisStorage, DefaultKeyBuilder
from app.classes.database import DataBase

DB = DataBase()

_redis_server = os.environ.get("REDIS_SERVER")
if not _redis_server:
    raise Exception('Define REDIS_SERVER in .env file')
RD = redis.Redis.from_url( _redis_server, protocol=3, decode_responses=True )

_local_server = os.environ.get("LOCAL_SERVER")
if _local_server:
    local_server = TelegramAPIServer.from_base( _local_server, is_local=True )
    session = AiohttpSession( api=local_server )
else:
    session = AiohttpSession()

_token = os.environ.get("BOT_TOKEN")
if not _token:
    raise Exception('define BOT_TOKEN in .env file')
BOT = Bot(os.environ.get("BOT_TOKEN"), session=session)

kb = DefaultKeyBuilder(prefix='fsm', with_bot_id=True, with_destiny=True)
storage = RedisStorage( RD, key_builder=kb )

DP = Dispatcher(storage=storage)