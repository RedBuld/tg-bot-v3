import idna
import ujson
import aiohttp
import logging
from aiohttp.client_exceptions import ClientError
from aiogram import Dispatcher, Router, F, types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from app import models, variables, dto
from app.configs import GC
from app.objects import DB, RD, BOT
from app.classes.interconnect import Interconnect

logger = logging.getLogger( __name__ )

class MiscController:
    
    @staticmethod
    async def ShowAllowedSites( message: types.Message ) -> None:
        try:
            sites_list = await Interconnect.GetSitesActive()
            await BOT.send_message( chat_id=message.chat.id, text=f"Список поддерживаемых сайтов:\n\n" + ( '\n'.join( [idna.decode(x) for x in sites_list] ) ), reply_markup=None )
        except ClientError as e:
            await BOT.send_message( chat_id=message.chat.id, text="Ошибка соединения с сервером загрузки", reply_markup=None )
        except Exception as e:
            print(e)
            await BOT.send_message( chat_id=message.chat.id, text="Произошла ошика", reply_markup=None )


    @staticmethod
    async def GetMyUID( message: types.Message ) -> None:
        await BOT.send_message( chat_id=message.chat.id, text=f"Ваш ID: \n" + str( message.from_user.id ), reply_markup=None )


    @staticmethod
    async def StatsMenu( message: types.Message ) -> None:
        builder = InlineKeyboardBuilder()
        if GC.url:
            stats_web_app = types.WebAppInfo( url=GC.url + 'stats' )
            builder.button( text="Статистика сайтов", web_app=stats_web_app )
        if GC.url:
            usage_web_app = types.WebAppInfo( url=GC.url + 'usage' )
            builder.button( text="Загрузка очереди", web_app=usage_web_app )
        builder.button( text="Дневной лимит", callback_data="mc:daily" )
        builder.adjust(1, repeat=True)

        await BOT.send_message( chat_id=message.chat.id, text="Доступная статистика", reply_markup=builder.as_markup() )


    @staticmethod
    async def DailyLimit(callback_query: types.CallbackQuery ) -> None:
        await callback_query.answer()

        usage = await DB.GetUserUsage( user_id=callback_query.from_user.id )

        acl = await DB.GetACL( user_id=callback_query.from_user.id )

        limit = acl.getLimit() if acl else GC.free_limit

        await BOT.send_message( chat_id=callback_query.message.chat.id, text=f'Дневной лимит: {usage} / {limit}' )
