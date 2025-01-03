import logging
import idna
from typing import Any
from aiogram import Dispatcher, Router, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from app import variables, dto, models
from app.configs import GC
from app.objects import DB, RD, BOT

logger = logging.getLogger( __name__ )

class ExistentAuthController:

    @staticmethod
    async def Cancel( callback_query: types.CallbackQuery ):
        await callback_query.answer()

        try:
            await BOT.delete_message( chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id )
        except:
            pass
    
    @staticmethod
    async def ListAuthedSites( message: types.Message ):
        user_id = message.from_user.id

        sites = await DB.GetUserAuthedSites( user_id )

        if sites:
            builder = InlineKeyboardBuilder()

            for site in sites:
                builder.button( text=idna.decode(site), callback_data=f"eac:{site}" )

            builder.adjust( 1, repeat=True )

            await BOT.send_message( chat_id=message.chat.id, text="Выберите сайт", reply_markup=builder.as_markup() )
        else:
            builder = InlineKeyboardBuilder()
            builder.button( text="Закрыть", callback_data=f"eac:cancel" )
            builder.adjust( 1, repeat=True )
            await BOT.send_message( chat_id=message.chat.id, text='Нет сохраненных доступов', reply_markup=builder.as_markup() )


    @staticmethod
    async def AuthActions( callback_query: types.CallbackQuery ) -> None:
        await callback_query.answer()

        user_id = callback_query.from_user.id
        chat_id = callback_query.message.chat.id
        message_id = callback_query.message.message_id

        data = callback_query.data.split(':')

        if len(data) == 2:
            site = data[1]
            if site == 'all':
                await ExistentAuthController.__all_sites( user_id=user_id, chat_id=chat_id, message_id=message_id )
            else:
                await ExistentAuthController.__all_site_logins( user_id=user_id, chat_id=chat_id, message_id=message_id, site=site )

        elif len(data) == 3:
            site = data[1]
            auth_id = int(data[2])
            await ExistentAuthController.__single_site_login( user_id=user_id, chat_id=chat_id, message_id=message_id, site=site, auth_id=auth_id )

        elif len(data) == 4:
            site = data[1]
            auth_id = int(data[2])
            action = data[3]
            if action == 'delete':
                await DB.DeleteUserAuth( user_id=user_id, auth_id=auth_id )
                await ExistentAuthController.__all_site_logins( user_id=user_id, chat_id=chat_id, message_id=message_id, site=site )

    #

    @staticmethod
    async def __all_sites( user_id: int, chat_id: int, message_id: int ) -> None:
        sites = await DB.GetUserAuthedSites( user_id )

        if sites:
            builder = InlineKeyboardBuilder()

            for site in sites:
                builder.button( text=idna.decode(site), callback_data=f"eac:{site}" )

            builder.adjust( 1, repeat=True )

            await BOT.edit_message_text( chat_id=chat_id, message_id=message_id, text="Выберите сайт", reply_markup=builder.as_markup() )
        else:
            builder = InlineKeyboardBuilder()
            builder.button( text="Закрыть", callback_data=f"eac:cancel" )
            builder.adjust( 1, repeat=True )
            await BOT.edit_message_text( chat_id=chat_id, message_id=message_id, text='Нет сохраненных доступов', reply_markup=builder.as_markup() )


    @staticmethod
    async def __all_site_logins( user_id: int, chat_id: int, message_id: int, site: str ) -> None:

        uas = await DB.GetUserAuthsForSite( user_id=user_id, site=site )

        builder = InlineKeyboardBuilder()
        text = ''
        if uas:
            for ua in uas:
                builder.button( text=ua.get_name(), callback_data=f"eac:{site}:{ua.id}" )
            text = f'Список доступов для сайта {site}'
        else:
            text = f'Нет сохраненных доступов для сайта {site}'

        builder.button( text="Назад", callback_data=f"eac:all" )

        builder.adjust( 1, repeat=True )

        await BOT.edit_message_text( chat_id=chat_id, message_id=message_id, text=text, reply_markup=builder.as_markup() )


    @staticmethod
    async def __single_site_login( user_id: int, chat_id: int, message_id: int, site: str, auth_id: int ) -> None:

        ua = await DB.GetUserAuth( user_id=user_id, auth_id=auth_id )

        if ua:
            builder = InlineKeyboardBuilder()
            builder.button( text='Удалить', callback_data=f"eac:{site}:{ua.id}:delete" )
            builder.button( text="Назад", callback_data=f"eac:{site}" )
            builder.adjust( 1, repeat=True )
            await BOT.edit_message_text( chat_id=chat_id, message_id=message_id, text=f'Авторизация:\n\nЛогин: "{ua.login}"\nПароль: "{ua.password}"', reply_markup=builder.as_markup() )