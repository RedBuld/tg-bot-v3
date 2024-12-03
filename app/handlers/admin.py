import logging
import traceback
from typing import Any, Dict, List
from aiohttp.client_exceptions import ClientError
from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.exceptions import TelegramRetryAfter, TelegramMigrateToChat, TelegramBadRequest, TelegramNotFound, TelegramConflictError, TelegramUnauthorizedError, TelegramForbiddenError, TelegramServerError, RestartingTelegram, TelegramAPIError, TelegramEntityTooLarge, ClientDecodeError
from app import schemas
from app.configs import GC
from app.objects import BOT, DB
from app.classes.interconnect import Interconnect

logger = logging.getLogger( __name__ )

class AdminController:

    @staticmethod
    async def set_menu() -> None:

        commands = [
            types.BotCommand( command='sites', description='Посмотреть доступные сайты' ),
            types.BotCommand( command='auth', description='Добавить авторизацию' ),
            types.BotCommand( command='auths', description='Список авторизаций' ),
            types.BotCommand( command='setup', description='Настройки' ),
            types.BotCommand( command='stats', description='Статистика' )
        ]

        await BOT.set_my_commands(commands=commands, scope=types.BotCommandScopeDefault())

        commands.append( types.BotCommand( command='admin_reload', description='Перезагрузка конфигурации' ) )
        commands.append( types.BotCommand( command='admin_queue', description='Очередь' ) )

        for admin_id in GC.admins:
            await BOT.set_my_commands(commands=commands, scope=types.BotCommandScopeChat(chat_id=admin_id))
    
    @staticmethod
    async def admin_cancel_command( message: types.Message ) -> None:

        if message.from_user.id not in GC.admins:
            return await BOT.send_message( chat_id=message.chat.id, text="Недостаточно прав" )

        task_id = int( message.text.split('/admin_cancel')[1] )

        if not task_id:
            return

        request = schemas.DownloadCancelRequest(
            task_id = task_id
        )

        result = await Interconnect.CancelDownload( request )
        if type(result) != bool:
            await BOT.send_message( chat_id=message.chat.id, text=str(result) )
        try:
            await BOT.delete_message( chat_id=message.chat.id, message_id=message.message_id )
        except:
            await BOT.send_message( chat_id=message.chat.id, reply_to_message_id=message.message_id, text="Ошибка: Не могу удалить сообщение" )

    @staticmethod
    async def admin_cancel_batch_command( message: types.Message ) -> None:

        if message.from_user.id not in GC.admins:
            return await BOT.send_message( chat_id=message.chat.id, text="Недостаточно прав" )

        tasks_ids = message.text.split('/admin_cancel_batch')[1].split(',')

        if not tasks_ids:
            return

        for task_id in tasks_ids:
            request = schemas.DownloadCancelRequest(
                task_id = int( task_id )
            )

            result = await Interconnect.CancelDownload( request )
            if type(result) != bool:
                await BOT.send_message( chat_id=message.chat.id, text=str(result) )
        try:
            await BOT.delete_message( chat_id=message.chat.id, message_id=message.message_id )
        except:
            await BOT.send_message( chat_id=message.chat.id, reply_to_message_id=message.message_id, text="Ошибка: Не могу удалить сообщение" )

    @staticmethod
    async def admin_reload_command( message: types.Message ) -> None:

        if message.from_user.id not in GC.admins:
            return await BOT.send_message( chat_id=message.chat.id, text="Недостаточно прав" )

        await Interconnect.ReloadConfig()

        await AdminController.set_menu()

    @staticmethod
    async def admin_leave_command( message: types.Message ) -> None:

        if message.from_user.id not in GC.admins:
            return await BOT.send_message( chat_id=message.chat.id, text="Недостаточно прав" )

        chat_id = message.text.split('/admin_leave')[1]

        await BOT.leave_chat( chat_id=chat_id )

        
    @staticmethod
    async def admin_queue( message: types.Message ) -> None:
        
        message = await BOT.send_message( chat_id=message.chat.id, text='Очередь', disable_web_page_preview=True )

        await AdminController.__update_queue_inline(message)

    @staticmethod
    async def admin_queue_pass( callback_query: types.CallbackQuery ) -> None:
        await callback_query.answer()

    @staticmethod
    async def admin_queue_refresh( callback_query: types.CallbackQuery ) -> None:
        await callback_query.answer()

        await AdminController.__update_queue_inline(callback_query.message)

    @staticmethod
    async def admin_queue_cancel( callback_query: types.CallbackQuery ) -> None:
        await callback_query.answer()

        task_id = int( callback_query.data.split('aq:cancel:')[1] )

        request = schemas.DownloadCancelRequest(
            task_id = int( task_id )
        )

        result = await Interconnect.CancelDownloadWithObj( request )
        if type(result) != bool:
            try:
                await BOT.delete_message( chat_id=result.chat_id, message_id=result.message_id )
            except:
                pass

        await AdminController.__update_queue_inline(callback_query.message)


    @staticmethod
    async def __update_queue_inline( message: types.Message ) -> None:

        tasks = await Interconnect.GetUsage()

        builder = InlineKeyboardBuilder()

        filler = "-"*10
        
        builder.button( text="Отмена", callback_data="aq:cancel" )
        builder.button( text="Обновить", callback_data="aq:refresh" )

        builder.button( text="Загружаются", callback_data="aq:pass" )
        builder.button( text='', callback_data="aq:pass" )
        for group in tasks['running']:
            for task in group['tasks']:
                builder.button( text=task['last_status'], callback_data="aq:pass" )
                builder.button( text='', callback_data="aq:pass" )
                # 
                builder.button( text=task['url'], url=task['url'] )
                builder.button( text='🚫', callback_data=f"aq:cancel:{task['task_id']}" )

        builder.button( text="Ждут", callback_data="aq:pass" )
        builder.button( text='', callback_data="aq:pass" )
        for group in tasks['waiting']:
            for task in group['tasks']:
                builder.button( text=task['url'], url=task['url'] )
                builder.button( text='🚫', callback_data=f"aq:cancel:{task['task_id']}" )
        
        builder.adjust( 2, repeat=True )

        try:
            await BOT.edit_message_text( chat_id=message.chat.id, text='Очередь', message_id=message.message_id, disable_web_page_preview=True, reply_markup=builder.as_markup() )
        except TelegramBadRequest as e:
            if 'message to edit not foun' in str(e):
                _ignore = True
            if 'message is not modified' in str(e):
                _ignore = True
            if 'chat not found' in str(e):
                _ignore = True
            if 'web App buttons' in str(e):
                _ignore = True
            if 'not enough rights' in str(e):
                _ignore = True
            pass
            if not _ignore:
                traceback.print_exc()
        except:
            traceback.print_exc()
        return True