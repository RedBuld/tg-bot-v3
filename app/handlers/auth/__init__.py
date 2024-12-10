import idna
import logging
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from app import variables
from app.configs import GC
from app.objects import DB, RD, BOT
from app.classes.interconnect import Interconnect
from app.handlers.auth.inline import InlineAuthController
from app.handlers.auth.window import WindowAuthController

logger = logging.getLogger( __name__ )

class AuthController:
        
    @staticmethod
    async def auth_cancel( callback_query: types.CallbackQuery, state: FSMContext ):
        await callback_query.answer()

        auth = await state.get_data()
        if auth and 'base_message' in auth and auth['base_message']:    
            try:
                await BOT.delete_message( chat_id=callback_query.message.chat.id, message_id=auth['base_message'] )
            except:
                pass
        if auth and 'last_message' in auth and auth['last_message']:
            try:
                await BOT.delete_message( chat_id=callback_query.message.chat.id, message_id=auth['last_message'] )
            except:
                pass

        await state.clear()

        try:
            await BOT.delete_message( chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id )
        except:
            pass


    @staticmethod
    async def auth_init( message: types.Message, state: FSMContext ):

        actual_state = await state.get_state()
        if actual_state and actual_state.startswith( 'AuthForm' ):
            await BOT.send_message( chat_id=message.chat.id, text="Отмените или завершите предыдущую авторизацию" )
        
        sites_with_auth = await Interconnect.GetSitesWithAuth()

        if len(sites_with_auth) > 0:
            builder = InlineKeyboardBuilder()

            for site in sites_with_auth:
                builder.button( text=idna.decode(site), callback_data=f"auth:{site}" )

            builder.adjust(1, repeat=True)

            await state.set_state(variables.AuthForm.site)

            msg = await BOT.send_message( chat_id=message.chat.id, text="Выберите сайт", reply_markup=builder.as_markup() )
            await state.update_data( base_message=msg.message_id )
        else:
            await state.clear()
            await BOT.send_message( chat_id=message.chat.id, text="Нет сайтов доступных для авторизации", reply_markup=None )


    @staticmethod
    async def auth_setup_site( callback_query: types.CallbackQuery, state: FSMContext ) -> None:
        await callback_query.answer()

        site = callback_query.data.split('auth:')[1]

        user = await DB.getUser( user_id=callback_query.from_user.id )

        if not user or not user.setuped:
            await BOT.send_message( chat_id=callback_query.message.chat.id, text="Завершите настройку" )
            return

        if user.interact_mode == 0 or not GC.bot_host:
            await state.update_data(site=site)
            await InlineAuthController.init( callback_query, user, site, state )
            return
        elif user.interact_mode == 1:
            await state.clear()
            await WindowAuthController.init( callback_query, user, site )
            return