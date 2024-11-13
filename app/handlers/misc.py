import idna
import ujson
import aiohttp
import logging
from aiohttp.client_exceptions import ClientError
from aiogram import Dispatcher, Router, F, types
from aiogram.types import ReplyKeyboardRemove
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from app import models, variables, schemas
from app.configs import GC
from app.objects import DB, RD, BOT

logger = logging.getLogger( __name__ )

class MiscController:
    
    async def get_sites_list( self ):
        async with aiohttp.ClientSession( json_serialize=ujson.dumps ) as session:
            async with session.post( GC.queue_host + 'sites/active', verify_ssl=False ) as response:
                if response.status == 200:
                    data = await response.json( loads=ujson.loads )
                    res = schemas.SiteListResponse( **data )
                    return res.sites

    async def sites_command( self, message: types.Message ) -> None:
        try:
            sites_list = await self.get_sites_list()
            await BOT.send_message( chat_id=message.chat.id, text=f"Список поддерживаемых сайтов:\n\n" + ( '\n'.join( [idna.decode(x) for x in sites_list] ) ), reply_markup=None )
        except ClientError as e:
            await BOT.send_message( chat_id=message.chat.id, text="Ошибка соединения с сервером загрузки", reply_markup=None )
        except Exception as e:
            print(e)
            await BOT.send_message( chat_id=message.chat.id, text="Произошла ошика", reply_markup=None )


    async def uid_command( self, message: types.Message ) -> None:

        await BOT.send_message( chat_id=message.chat.id, text=f"Ваш ID: \n" + str( message.from_user.id ), reply_markup=None )