import idna
import ujson
import aiohttp
import logging
import traceback
from aiohttp.client_exceptions import ClientError
from aiogram import Dispatcher, Router, F, types
from aiogram.fsm.context import FSMContext
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
            groups = await Interconnect.GetSitesActiveGrouped()

            text = 'Список поддерживаемых сайтов:'

            for group, sites_list in groups.items():
                name = GC.groups[ group ] if group in GC.groups else group
                sites = '\n'.join( [ idna.decode(x) for x in sites_list ] )
                text += f'\n\n<b>{name}</b>:\n\n{sites}'

            await BOT.send_message( chat_id=message.chat.id, text=text, parse_mode="HTML", reply_markup=None )
        except ClientError as e:
            await BOT.send_message( chat_id=message.chat.id, text="Ошибка соединения с сервером загрузки", reply_markup=None )
        except Exception as e:
            traceback.print_exc()
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
    async def DailyLimit( callback_query: types.CallbackQuery ) -> None:
        await callback_query.answer()

        usage = await DB.GetUserUsage( user_id=callback_query.from_user.id )

        acl = await DB.GetACL( user_id=callback_query.from_user.id )

        limit = acl.getLimit() if acl else GC.free_limit

        await BOT.send_message( chat_id=callback_query.message.chat.id, text=f'Дневной лимит: {usage} / {limit}' )


    @staticmethod
    async def Panic( message: types.Message, state: FSMContext ) -> None:

        text = "Состояний не найдено"
        instruction = '\n\nСначала попробуйте завершить или отменить в сообщении которое отметил бот.\nТОЛЬКО если сообщения нет - нажимайте сброс'

        reply_to = None
        show_button = False

        actual_state = await state.get_state()

        if actual_state:
            show_button = True
            state_data = await state.get_data()

            if actual_state.startswith( 'AuthForm' ):
                text = "Отмените или завершите предыдущую авторизацию"
                if 'base_message' in state_data and state_data[ 'base_message' ]:
                    reply_to = state_data[ 'base_message' ]
                    text += instruction

            elif actual_state.startswith( 'SetupAccount' ):
                text = "Отмените или завершите настройку аккаунта"
                if 'base_message' in state_data and state_data[ 'base_message' ]:
                    reply_to = state_data[ 'base_message' ]
                    text += instruction

            elif actual_state.startswith( 'SetupSite' ):
                text = "Отмените или завершите настройку сайта"
                if 'base_message' in state_data and state_data[ 'base_message' ]:
                    reply_to = state_data[ 'base_message' ]
                    text += instruction

            elif actual_state.startswith( 'InlineDownload' ):
                text = "Отмените или завершите настройку загрузки"
                if 'base_message' in state_data and state_data[ 'base_message' ]:
                    reply_to = state_data[ 'base_message' ]
                    text += instruction

            else:
                text = "Нажмите сброс"

        if show_button:
            builder = InlineKeyboardBuilder()
            builder.button( text='Сброс', callback_data='panic:reset')
            await BOT.send_message( chat_id=message.chat.id, text=text, reply_to_message_id=reply_to, reply_markup=builder.as_markup() )
        else:
            await BOT.send_message( chat_id=message.chat.id, text=text )


    @staticmethod
    async def PanicReset( callback_query: types.CallbackQuery, state: FSMContext ) -> None:
        await state.clear()
        await BOT.send_message( chat_id=callback_query.message.chat.id, text="Состояние сброшено" )