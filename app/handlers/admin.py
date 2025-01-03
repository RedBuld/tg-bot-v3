import logging
import traceback
from typing import Any, Dict, List
from aiohttp.client_exceptions import ClientError
from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.exceptions import TelegramRetryAfter, TelegramMigrateToChat, TelegramBadRequest, TelegramNotFound, TelegramConflictError, TelegramUnauthorizedError, TelegramForbiddenError, TelegramServerError, RestartingTelegram, TelegramAPIError, TelegramEntityTooLarge, ClientDecodeError
from app import dto, variables
from app.configs import GC
from app.objects import BOT, RD
from app.classes.interconnect import Interconnect

logger = logging.getLogger( __name__ )

class AdminController:

    @staticmethod
    async def SetBotMenu() -> None:

        commands = [
            types.BotCommand( command='sites', description='Посмотреть доступные сайты' ),
            types.BotCommand( command='auths', description='Список авторизаций' ),
            types.BotCommand( command='auth', description='Добавить авторизацию' ),
            types.BotCommand( command='setup_global', description='Настройки аккаунта' ),
            types.BotCommand( command='setup_sites', description='Настройки для сайтов' ),
            types.BotCommand( command='panic', description='Паника' ),
            types.BotCommand( command='stats', description='Статистика' ),
        ]

        await BOT.set_my_commands(commands=commands, scope=types.BotCommandScopeDefault())

        commands.append( types.BotCommand( command='admin_reload_dc', description='Перезагрузка конфигурации DC' ) )
        commands.append( types.BotCommand( command='admin_reload_bot', description='Перезагрузка конфигурации бота' ) )
        commands.append( types.BotCommand( command='admin_queue', description='Очередь' ) )
        commands.append( types.BotCommand( command='admin_stop_tasks', description='Стоп очереди тасков' ) )
        commands.append( types.BotCommand( command='admin_start_tasks', description='Старт очереди тасков' ) )
        commands.append( types.BotCommand( command='admin_stop_results', description='Стоп очереди результатов' ) )
        commands.append( types.BotCommand( command='admin_start_results', description='Старт очереди результатов' ) )
        commands.append( types.BotCommand( command='admin_stop_queue', description='Стоп очереди' ) )
        commands.append( types.BotCommand( command='admin_start_queue', description='Старт очереди' ) )

        for admin_id in GC.admins:
            try:
                await BOT.set_my_commands(commands=commands, scope=types.BotCommandScopeChat(chat_id=admin_id))
            except:
                pass


    @staticmethod
    async def CancelTask( message: types.Message ) -> None:

        if message.from_user.id not in GC.admins:
            return await BOT.send_message( chat_id=message.chat.id, text="Недостаточно прав" )

        task_id = int( message.text.split('/admin_cancel')[1] )

        if not task_id:
            return

        request = dto.DownloadCancelRequest(
            task_id = task_id
        )

        result = await Interconnect.CancelDownload( request )
        if type(result) == str:
            try:
                await BOT.send_message( chat_id=message.chat.id, text=str(result) )
            except:
                pass
        else:
            try:
                await BOT.delete_message( chat_id=result.chat_id, message_id=result.message_id )
            except:
                await BOT.send_message( chat_id=message.chat.id, reply_to_message_id=message.message_id, text="Ошибка: Не могу удалить сообщение" )


    @staticmethod
    async def CancelTasks( message: types.Message ) -> None:

        if message.from_user.id not in GC.admins:
            return await BOT.send_message( chat_id=message.chat.id, text="Недостаточно прав" )

        tasks_ids = message.text.split('/admin_cancel_batch')[1].split(',')

        if not tasks_ids:
            return

        for task_id in tasks_ids:
            request = dto.DownloadCancelRequest(
                task_id = int( task_id )
            )

            result = await Interconnect.CancelDownload( request )
            if type(result) == str:
                try:
                    await BOT.send_message( chat_id=message.chat.id, text=str(result) )
                except:
                    pass
            else:
                try:
                    await BOT.delete_message( chat_id=result.chat_id, message_id=result.message_id )
                except:
                    pass
        try:
            await BOT.delete_message( chat_id=message.chat.id, message_id=message.message_id )
        except:
            await BOT.send_message( chat_id=message.chat.id, reply_to_message_id=message.message_id, text="Ошибка: Не могу удалить сообщение" )


    @staticmethod
    async def ReloadDownloadCenter( message: types.Message ) -> None:

        if message.from_user.id not in GC.admins:
            return await BOT.send_message( chat_id=message.chat.id, text="Недостаточно прав" )

        await Interconnect.ReloadConfig()

        await AdminController.SetBotMenu()

        await RD.delete(variables.ACTIVE_SITES_CACHE_KEY)
        await RD.delete(variables.AUTH_SITES_CACHE_KEY)


    @staticmethod
    async def ReloadBot( message: types.Message ) -> None:

        if message.from_user.id not in GC.admins:
            return await BOT.send_message( chat_id=message.chat.id, text="Недостаточно прав" )

        await RD.delete(variables.ACTIVE_SITES_CACHE_KEY)
        await RD.delete(variables.AUTH_SITES_CACHE_KEY)

        await AdminController.SetBotMenu()


    @staticmethod
    async def LeaveChat( message: types.Message ) -> None:

        if message.from_user.id not in GC.admins:
            return await BOT.send_message( chat_id=message.chat.id, text="Недостаточно прав" )

        chat_id = message.text.split('/admin_leave')[1]

        await BOT.leave_chat( chat_id=chat_id )


    @staticmethod
    async def StopTasks( message: types.Message ) -> None:
        await Interconnect.AdminStopTasks()
        pass


    @staticmethod
    async def StartTasks( message: types.Message ) -> None:
        await Interconnect.AdminStartTasks()
        pass


    @staticmethod
    async def StopResults( message: types.Message ) -> None:
        await Interconnect.AdminStopResults()
        pass


    @staticmethod
    async def StartResults( message: types.Message ) -> None:
        await Interconnect.AdminStartResults()
        pass


    @staticmethod
    async def StopQueue( message: types.Message ) -> None:
        await Interconnect.AdminStopQueue()
        pass


    @staticmethod
    async def StartQueue( message: types.Message ) -> None:
        await Interconnect.AdminStartQueue()
        pass
