import logging
from aiohttp.client_exceptions import ClientError
from aiogram import types
from app import schemas
from app.configs import GC
from app.objects import BOT
from app.classes.interconnect import Interconnect

logger = logging.getLogger( __name__ )

class AdminController:
    
    @staticmethod
    async def admin_cancel_command( message: types.Message ) -> None:

        if message.from_user.id not in GC.admins:
            return await BOT.send_message( chat_id=message.chat.id, text="Недостаточно прав" )

        task_id = int( message.text.split('/admin_cancel')[1] )

        request = schemas.DownloadCancelRequest(
            task_id = task_id
        )

        result = await Interconnect.CancelDownload( request )
        if type(result) == bool:
            try:
                await BOT.delete_message( chat_id=message.chat.id, message_id=message.message_id )
            except:
                await BOT.send_message( chat_id=message.chat.id, reply_to_message_id=message.message_id, text="Ошибка: Не могу удалить сообщение" )
        else:
            await BOT.send_message( chat_id=message.chat.id, text=str(result) )

    @staticmethod
    async def admin_reload_command( message: types.Message ) -> None:

        if message.from_user.id not in GC.admins:
            return await BOT.send_message( chat_id=message.chat.id, text="Недостаточно прав" )

        await Interconnect.ReloadConfig()

    @staticmethod
    async def admin_leave_command( message: types.Message ) -> None:

        if message.from_user.id not in GC.admins:
            return await BOT.send_message( chat_id=message.chat.id, text="Недостаточно прав" )

        chat_id = message.text.split('/admin_leave')[1]

        await BOT.leave_chat( chat_id=chat_id )