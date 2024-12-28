import asyncio
import logging
import ujson
import urllib
import traceback
from typing import Any
from cryptography.fernet import Fernet
from aiogram import Dispatcher, Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from app import variables, dto, models
from app.configs import GC
from app.objects import DB, RD, BOT

logger = logging.getLogger( __name__ )

class WindowAuthController:

    @staticmethod
    async def startAuthForSite( callback_query: types.CallbackQuery, user: models.User, site: str ) -> None:
        data = {
            'site': site,
            'user_id': callback_query.from_user.id,
            'chat_id': callback_query.message.chat.id,
            'message_id': callback_query.message.message_id,
        }

        fernet = Fernet( GC.encrypt_key )
        encrypted = fernet.encrypt( ujson.dumps(data).encode('utf-8') )
        web_app = types.WebAppInfo( url=GC.url + 'auth/setup?payload=' + urllib.parse.quote_plus( encrypted.decode('utf-8') ) )

        builder = InlineKeyboardBuilder()
        builder.button( text="Добавить", web_app=web_app )
        builder.button( text="Отмена", callback_data="auth:cancel" )
        builder.adjust( 1, repeat=True )

        await BOT.edit_message_text( chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id, text=f'Добавление авторизации для сайта {site}', reply_markup=builder.as_markup() )


    @staticmethod
    async def Save( payload: dto.AuthSetupRequest ) -> None:
        try:
            auth = await DB.SaveUserAuth( user_id=payload.user_id, site=payload.site, login=payload.login, password=payload.password )
            logger.info(auth)
        except Exception as e:
            logger.error(str(e))
            await BOT.send_message( chat_id=payload.chat_id, text=f'Произошла ошибка. Попробуйте позднее', reply_markup=None)
            return False


        await BOT.delete_message( chat_id=payload.chat_id, message_id=payload.message_id)
        await BOT.send_message( chat_id=payload.chat_id, text=f'Авторизация для сайта {payload.site} сохранена', reply_markup=None)
        return True