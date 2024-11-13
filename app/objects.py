import os
import redis.asyncio as redis
from aiogram import Bot
from aiogram import Dispatcher
from aiogram.client.telegram import TelegramAPIServer
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.fsm.storage.redis import RedisStorage, DefaultKeyBuilder
from app.classes.database import DataBase
from app.classes.interconnect import Interconnect

DB = DataBase()

IC = Interconnect()

RD = redis.Redis( host='127.0.0.1', port=6379, db=0, protocol=3, decode_responses=True )

local_server = TelegramAPIServer.from_base( 'http://localhost:4041', is_local=True )
session = AiohttpSession( api=local_server )
BOT = Bot(os.environ.get("BOT_TOKEN"), session=session)

kb = DefaultKeyBuilder(prefix='fsm', with_bot_id=True, with_destiny=True)
storage = RedisStorage( RD, key_builder=kb )
DP = Dispatcher(storage=storage)