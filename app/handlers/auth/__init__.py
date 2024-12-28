import idna
import logging
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from app import variables
from app.configs import GC
from app.objects import DB, RD, BOT
from app.tools import stateChecker, punyDecode
from app.classes.interconnect import Interconnect
from app.handlers.auth.inline import InlineAuthController
from app.handlers.auth.window import WindowAuthController

logger = logging.getLogger( __name__ )

class AuthController:

    @staticmethod
    async def StartAuth( message: types.Message, state: FSMContext ) -> None:

        if message.chat.type != 'private':
            await BOT.send_message( chat_id=message.chat.id, text="Авторизация возможна только в диалоге с ботом" )
            return

        alert = await stateChecker( state )
        if alert is not None:
            await BOT.send_message( chat_id=message.chat.id, text=alert )
            return
        
        sites_with_auth = await Interconnect.GetSitesWithAuth()

        if len( sites_with_auth ) > 0:
            builder = InlineKeyboardBuilder()

            for site in sites_with_auth:
                builder.button( text=punyDecode( site ), callback_data=f"auth:{site}" )

            builder.adjust( 1, repeat=True )

            await state.set_state( variables.AuthForm.site )

            msg = await BOT.send_message( chat_id=message.chat.id, text="Выберите сайт", reply_markup=builder.as_markup() )
            await state.update_data( base_message=msg.message_id )
        else:
            await state.clear()
            await BOT.send_message( chat_id=message.chat.id, text="Нет сайтов доступных для авторизации", reply_markup=None )


    @staticmethod
    async def CancelAuth( callback_query: types.CallbackQuery, state: FSMContext ):
        await callback_query.answer()

        active_state = await state.get_data()
        if active_state and active_state.startswith( 'AuthForm' ):
            if 'base_message' in active_state and active_state[ 'base_message' ]:    
                try:
                    await BOT.delete_message( chat_id=callback_query.message.chat.id, message_id=active_state[ 'base_message' ] )
                except:
                    pass
            if 'last_message' in active_state and active_state[ 'last_message' ]:
                try:
                    await BOT.delete_message( chat_id=callback_query.message.chat.id, message_id=active_state[ 'last_message' ] )
                except:
                    pass
            await state.clear()

        try:
            await BOT.delete_message( chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id )
        except:
            pass


    @staticmethod
    async def SelectSite( callback_query: types.CallbackQuery, state: FSMContext ) -> None:
        await callback_query.answer()

        site = callback_query.data.split( 'auth:' )[ 1 ]

        user = await DB.GetUser( user_id=callback_query.from_user.id )

        if not user or not user.setuped:
            await BOT.send_message( chat_id=callback_query.message.chat.id, text="Завершите настройку" )
            return

        if user.interact_mode == 0 or not GC.url:
            await state.update_data( site=site )
            await InlineAuthController.startAuthForSite( callback_query, user, site, state )
            return

        elif user.interact_mode == 1:
            await state.clear()
            await WindowAuthController.startAuthForSite( callback_query, user, site )
            return