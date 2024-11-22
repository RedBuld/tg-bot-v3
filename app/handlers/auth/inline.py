import asyncio
import logging
import traceback
from typing import Any
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from app import variables, schemas, models
from app.configs import GC
from app.objects import DB, RD, BOT

logger = logging.getLogger( __name__ )

class InlineAuthController:

    @staticmethod
    async def init( callback_query: types.CallbackQuery, user: models.User, site: str, state: FSMContext ) -> None:
        await state.set_state(variables.AuthForm.login)

        builder = InlineKeyboardBuilder()
        builder.button( text="Отмена", callback_data=f"auth:cancel" )
        builder.adjust(1, repeat=True)

        await BOT.edit_message_text( chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id, text=f'Выбран сайт {site}\n\n!!!ВХОД ЧЕРЕЗ СОЦ. СЕТИ НЕВОЗМОЖЕН!!!', reply_markup=builder.as_markup())

        msg = await BOT.send_message( chat_id=callback_query.message.chat.id, text=f'Отправьте сообщением логин')
        await state.update_data(last_message=msg.message_id)

    @staticmethod
    async def inline_auth_login( message: types.Message, state: FSMContext ) -> None:

        login = message.text.strip()

        await BOT.delete_message( chat_id=message.chat.id, message_id=message.message_id )

        if not login.startswith('/') and not login.startswith('http:') and not login.startswith('https:'):

            await state.update_data(login=login)
        
            auth = await state.get_data()
            await BOT.delete_message( chat_id=message.chat.id, message_id=auth['last_message'] )

            await state.set_state(variables.AuthForm.password)

            msg = await BOT.send_message( chat_id=message.chat.id, text=f'Отправьте сообщением пароль' )
            await state.update_data(last_message=msg.message_id)

    @staticmethod
    async def inline_auth_password( message: types.Message, state: FSMContext ) -> None:

        password = message.text #.strip()

        await BOT.delete_message( chat_id=message.chat.id, message_id=message.message_id )

        if not password.startswith('/') and not password.startswith('http:') and not password.startswith('https:'):

            await state.update_data(password=password)
        
            auth = await state.get_data()
            await BOT.delete_message( chat_id=message.chat.id, message_id=auth['last_message'] )

            await state.clear()

            if auth and 'base_message' in auth and auth['base_message']:    
                try:
                    await BOT.delete_message( chat_id=message.chat.id, message_id=auth['base_message'] )
                except:
                    pass

            if auth and 'last_message' in auth and auth['last_message']:
                try:
                    await BOT.delete_message( chat_id=message.chat.id, message_id=auth['last_message'] )
                except:
                    pass

            await DB.saveUserAuth( user_id=message.from_user.id, site=auth['site'], login=auth['login'], password=auth['password'] )

            await BOT.send_message( chat_id=message.chat.id, text=f'Авторизация для сайта {auth["site"]} сохранена', reply_markup=None)