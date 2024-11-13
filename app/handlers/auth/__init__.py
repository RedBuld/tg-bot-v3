import idna
import logging
import ujson
import aiohttp
from python_event_bus import EventBus
from aiogram import Dispatcher, Router, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from app import variables, schemas
from app.configs import GC
from app.objects import DB, RD, BOT

logger = logging.getLogger( __name__ )

class AuthController:
    
    async def _get_sites_with_auth( self ) -> bool:
        async with aiohttp.ClientSession( json_serialize=ujson.dumps ) as session:
            async with session.post( GC.queue_host + 'sites/auths', verify_ssl=False ) as response:
                if response.status == 200:
                    data = await response.json( loads=ujson.loads )
                    res = schemas.SiteListResponse( **data )
                    return res.sites
    
    #
    
    async def auth_cancel( self, callback_query: types.CallbackQuery, state: FSMContext ):
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


    async def auth_init( self, message: types.Message, state: FSMContext ):

        actual_state = await state.get_state()
        if actual_state and actual_state.startswith( 'AuthForm' ):
            await BOT.send_message( chat_id=message.chat.id, text="Отмените или завершите предыдущую авторизацию" )
        
        sites_with_auth = await self._get_sites_with_auth()

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


    async def auth_setup_site( self, callback_query: types.CallbackQuery, state: FSMContext ) -> None:
        await callback_query.answer()

        site = callback_query.data.split('auth:')[1]

        user = await DB.getUser( user_id=callback_query.from_user.id )

        if not user or not user.setuped:
            await BOT.send_message( chat_id=callback_query.message.chat.id, text="Завершите настройку" )
            return

        if user.interact_mode == 0:
            await state.update_data(site=site)
            EventBus.call("iac_init", callback_query, user, site, state)
            return
        elif user.interact_mode == 1:
            await state.clear()
            EventBus.call("wac_init", callback_query, user, site)
            return