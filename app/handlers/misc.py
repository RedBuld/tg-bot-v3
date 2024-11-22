import idna
import ujson
import aiohttp
import logging
from aiohttp.client_exceptions import ClientError
from aiogram import Dispatcher, Router, F, types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from app import models, variables, schemas
from app.configs import GC
from app.objects import DB, RD, BOT
from app.classes.interconnect import Interconnect

logger = logging.getLogger( __name__ )

class MiscController:
    
    @staticmethod
    async def sites_command( message: types.Message ) -> None:
        try:
            sites_list = await Interconnect.GetSitesActive()
            await BOT.send_message( chat_id=message.chat.id, text=f"Список поддерживаемых сайтов:\n\n" + ( '\n'.join( [idna.decode(x) for x in sites_list] ) ), reply_markup=None )
        except ClientError as e:
            await BOT.send_message( chat_id=message.chat.id, text="Ошибка соединения с сервером загрузки", reply_markup=None )
        except Exception as e:
            print(e)
            await BOT.send_message( chat_id=message.chat.id, text="Произошла ошика", reply_markup=None )


    @staticmethod
    async def uid_command( message: types.Message ) -> None:

        await BOT.send_message( chat_id=message.chat.id, text=f"Ваш ID: \n" + str( message.from_user.id ), reply_markup=None )
    
    @staticmethod
    async def stats_command( message: types.Message ) -> None:

        stats_web_app = types.WebAppInfo( url=GC.bot_host + 'stats' )
        usage_web_app = types.WebAppInfo( url=GC.bot_host + 'usage' )

        builder = InlineKeyboardBuilder()
        builder.button( text="Статистика сайтов", web_app=stats_web_app )
        builder.button( text="Загрузка очереди", web_app=usage_web_app )
        builder.adjust(1, repeat=True)

        await BOT.send_message( chat_id=message.chat.id, text="Доступная статистика", reply_markup=builder.as_markup() )