import os
import logging
import asyncio
from aiogram import Dispatcher, Router, F, types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from app import models
from app.configs import GC
from app.objects import DB, RD, BOT
from app.variables import InteractionModes, HashtagsModes

logger = logging.getLogger( __name__ )

class AccountSetupController:

    @staticmethod
    async def start_command( message: types.Message ) -> None:

        if message.from_user.is_bot != False:
            return

        try:
            user = await asyncio.wait_for( DB.getUser( message.from_user.id ), 5 )
        except TimeoutError as e:
            return await BOT.send_message( chat_id=message.chat.id, text="Ошибка соединения с БД. Попробуйте позднее" )

        uname = message.from_user.username
        if not uname:
            uname = message.from_user.first_name

        if not user:
            user = models.User(
                id=message.from_user.id,
                username=uname
            )
            try:
                user = await asyncio.wait_for( DB.saveUser(user), 5 )
            except TimeoutError as e:
                return await BOT.send_message( chat_id=message.chat.id, text="Ошибка соединения с БД. Попробуйте позднее" )
        
        try:
            user = await asyncio.wait_for( DB.getUser( message.from_user.id ), 5 )
        except TimeoutError as e:
            return await BOT.send_message( chat_id=message.chat.id, text="Ошибка соединения с БД. Попробуйте позднее" )

        if not user:
            return await BOT.send_message( chat_id=message.chat.id, text="Ошибка: пользователь не найден, нажмите /start" )

        text = f"Привет, {uname}. Проведем настройку?"
        if not user.setuped:
            text += "\n\n<em>В первый раз необходимо завершить настройку до конца</em>"

        builder = InlineKeyboardBuilder()
        builder.button( text="Да", callback_data=f"setup:start" )
        if user.setuped:
            builder.button( text="Нет", callback_data=f"setup:cancel" )
        builder.adjust(1, repeat=True)

        await BOT.send_message( chat_id=message.chat.id, text=text, parse_mode='HTML', reply_markup=builder.as_markup() )
    
    @staticmethod
    async def setup_command( message: types.Message ) -> None:

        text = "Что настроим?"

        builder = InlineKeyboardBuilder()
        builder.button( text="Режим взаимодействия", callback_data="setup:mode" )
        builder.button( text="Формат", callback_data="setup:format" )
        builder.button( text="Обложка", callback_data="setup:cover" )
        builder.button( text="Изображения", callback_data="setup:images" )
        builder.button( text="Хэштэги", callback_data="setup:hashtags" )
        builder.adjust(1, repeat=True)

        await BOT.send_message( chat_id=message.chat.id, text=text, reply_markup=builder.as_markup() )


    # callbacks


    @staticmethod
    async def account_setup_cancel( callback_query: types.CallbackQuery ) -> None:
        await callback_query.answer()

        try:
            await BOT.delete_message( chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id )
        except:
            await BOT.send_message( chat_id=callback_query.message.chat.id, reply_to_message_id=callback_query.message.message_id, text="Ошибка: Не могу удалить сообщение" )


    @staticmethod
    async def account_setup_start( callback_query: types.CallbackQuery ) -> None:
        await callback_query.answer()

        try:
            await BOT.delete_message( chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id )
        except:
            await BOT.send_message( chat_id=callback_query.message.chat.id, reply_to_message_id=callback_query.message.message_id, text="Ошибка: Не могу удалить сообщение" )
        
        await AccountSetupController.__setup_mode_start( callback_query.message.chat.id, callback_query.from_user.id )


    @staticmethod
    async def account_setup_mode( callback_query: types.CallbackQuery ) -> None:
        await callback_query.answer()

        try:
            await BOT.delete_message( chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id )
        except:
            await BOT.send_message( chat_id=callback_query.message.chat.id, reply_to_message_id=callback_query.message.message_id, text="Ошибка: Не могу удалить сообщение" )

        await AccountSetupController.__setup_mode_start( callback_query.message.chat.id, callback_query.from_user.id )


    @staticmethod
    async def account_setup_format( callback_query: types.CallbackQuery ) -> None:
        await callback_query.answer()

        try:
            await BOT.delete_message( chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id )
        except:
            await BOT.send_message( chat_id=callback_query.message.chat.id, reply_to_message_id=callback_query.message.message_id, text="Ошибка: Не могу удалить сообщение" )

        await AccountSetupController.__setup_format_start( callback_query.message.chat.id, callback_query.from_user.id )


    @staticmethod
    async def account_setup_cover( callback_query: types.CallbackQuery ) -> None:
        await callback_query.answer()

        try:
            await BOT.delete_message( chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id )
        except:
            await BOT.send_message( chat_id=callback_query.message.chat.id, reply_to_message_id=callback_query.message.message_id, text="Ошибка: Не могу удалить сообщение" )

        await AccountSetupController.__setup_cover_start( callback_query.message.chat.id, callback_query.from_user.id )


    @staticmethod
    async def account_setup_images( callback_query: types.CallbackQuery ) -> None:
        await callback_query.answer()

        try:
            await BOT.delete_message( chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id )
        except:
            await BOT.send_message( chat_id=callback_query.message.chat.id, reply_to_message_id=callback_query.message.message_id, text="Ошибка: Не могу удалить сообщение" )

        await AccountSetupController.__setup_images_start( callback_query.message.chat.id, callback_query.from_user.id )

    @staticmethod
    async def account_setup_hashtags( callback_query: types.CallbackQuery ) -> None:
        await callback_query.answer()

        try:
            await BOT.delete_message( chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id )
        except:
            await BOT.send_message( chat_id=callback_query.message.chat.id, reply_to_message_id=callback_query.message.message_id, text="Ошибка: Не могу удалить сообщение" )

        await AccountSetupController.__setup_hashtags_start( callback_query.message.chat.id, callback_query.from_user.id )


    # savers


    @staticmethod
    async def account_setup_mode_save( callback_query: types.CallbackQuery ) -> None:
        await callback_query.answer()

        try:
            await BOT.delete_message( chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id )
        except:
            await BOT.send_message( chat_id=callback_query.message.chat.id, reply_to_message_id=callback_query.message.message_id, text="Ошибка: Не могу удалить сообщение" )

        try:
            user = await asyncio.wait_for( DB.getUser( callback_query.from_user.id ), 5 )
        except TimeoutError as e:
            return await BOT.send_message( chat_id=callback_query.message.chat.id, text="Ошибка соединения с БД. Попробуйте позднее" )

        if not user:
            logger.info('mode_save')
            logger.info(callback_query)
            return await BOT.send_message( chat_id=callback_query.message.chat.id, text="Ошибка: пользователь не найден, нажмите /start" )

        _mode = callback_query.data.split('setup:mode:')[1]
        if _mode == 'inline':
            user.interact_mode = 0
        if _mode == 'windowed':
            user.interact_mode = 1

        try:
            user = await asyncio.wait_for( DB.saveUser(user), 5 )
        except TimeoutError as e:
            return await BOT.send_message( chat_id=callback_query.message.chat.id, text="Ошибка соединения с БД. Попробуйте позднее" )

        if not user:
            logger.info('mode_save')
            logger.info(callback_query)
            return await BOT.send_message( chat_id=callback_query.message.chat.id, text="Ошибка: пользователь не найден, нажмите /start" )
        
        if not user.setuped:
            await AccountSetupController.__setup_format_start( callback_query.message.chat.id, callback_query.from_user.id )
        else:
            return await BOT.send_message( chat_id=callback_query.message.chat.id, text="Сохранен режим взаимодействия: " + getattr(InteractionModes,_mode) )


    @staticmethod
    async def account_setup_format_save( callback_query: types.CallbackQuery ) -> None:
        await callback_query.answer()

        try:
            await BOT.delete_message( chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id )
        except:
            await BOT.send_message( chat_id=callback_query.message.chat.id, reply_to_message_id=callback_query.message.message_id, text="Ошибка: Не могу удалить сообщение" )
        
        try:
            user = await asyncio.wait_for( DB.getUser( callback_query.from_user.id ), 5 )
        except TimeoutError as e:
            return await BOT.send_message( chat_id=callback_query.message.chat.id, text="Ошибка соединения с БД. Попробуйте позднее" )

        if not user:
            logger.info('format_save')
            logger.info(callback_query)
            return await BOT.send_message( chat_id=callback_query.message.chat.id, text="Ошибка: пользователь не найден, нажмите /start" )
        user.format = callback_query.data.split('setup:format:')[1]
        try:
            user = await asyncio.wait_for( DB.saveUser(user), 5 )
        except TimeoutError as e:
            return await BOT.send_message( chat_id=callback_query.message.chat.id, text="Ошибка соединения с БД. Попробуйте позднее" )

        if not user.setuped:
            await AccountSetupController.__setup_cover_start( callback_query.message.chat.id, callback_query.from_user.id )
        else:
            return await BOT.send_message( chat_id=callback_query.message.chat.id, text="Сохранен формат по умолчанию: " + user.format )


    @staticmethod
    async def account_setup_cover_save( callback_query: types.CallbackQuery ) -> None:
        await callback_query.answer()

        try:
            await BOT.delete_message( chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id )
        except:
            await BOT.send_message( chat_id=callback_query.message.chat.id, reply_to_message_id=callback_query.message.message_id, text="Ошибка: Не могу удалить сообщение" )
        
        try:
            user = await asyncio.wait_for( DB.getUser( callback_query.from_user.id ), 5 )
        except TimeoutError as e:
            return await BOT.send_message( chat_id=callback_query.message.chat.id, text="Ошибка соединения с БД. Попробуйте позднее" )

        if not user:
            logger.info('cover_save')
            logger.info(callback_query)
            return await BOT.send_message( chat_id=callback_query.message.chat.id, text="Ошибка: пользователь не найден, нажмите /start" )
        _cover = callback_query.data.split('setup:cover:')[1]
        if _cover == 'yes':
            user.cover = True
        if _cover == 'no':
            user.cover = False
        try:
            user = await asyncio.wait_for( DB.saveUser(user), 5 )
        except TimeoutError as e:
            return await BOT.send_message( chat_id=callback_query.message.chat.id, text="Ошибка соединения с БД. Попробуйте позднее" )

        if not user.setuped:
            await AccountSetupController.__setup_images_start( callback_query.message.chat.id, callback_query.from_user.id )
        else:
            return await BOT.send_message( chat_id=callback_query.message.chat.id, text="Скачивание обложек по умолчанию: " + ('Да' if user.cover else 'Нет') )


    @staticmethod
    async def account_setup_images_save( callback_query: types.CallbackQuery ) -> None:
        await callback_query.answer()

        try:
            await BOT.delete_message( chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id )
        except:
            await BOT.send_message( chat_id=callback_query.message.chat.id, reply_to_message_id=callback_query.message.message_id, text="Ошибка: Не могу удалить сообщение" )
        
        try:
            user = await asyncio.wait_for( DB.getUser( callback_query.from_user.id ), 5 )
        except TimeoutError as e:
            return await BOT.send_message( chat_id=callback_query.message.chat.id, text="Ошибка соединения с БД. Попробуйте позднее" )

        if not user:
            logger.info('images_save')
            logger.info(callback_query)
            return await BOT.send_message( chat_id=callback_query.message.chat.id, text="Ошибка: пользователь не найден, нажмите /start" )
        _images = callback_query.data.split('setup:images:')[1]
        if _images == 'yes':
            user.images = True
        if _images == 'no':
            user.images = False
        try:
            user = await asyncio.wait_for( DB.saveUser(user), 5 )
        except TimeoutError as e:
            return await BOT.send_message( chat_id=callback_query.message.chat.id, text="Ошибка соединения с БД. Попробуйте позднее" )

        if not user.setuped:
            await AccountSetupController.__setup_hashtags_start( callback_query.message.chat.id, callback_query.from_user.id )
        else:
            return await BOT.send_message( chat_id=callback_query.message.chat.id, text="Скачивание изображений по умолчанию: " + ('Да' if user.images else 'Нет') )


    @staticmethod
    async def account_setup_hashtags_save( callback_query: types.CallbackQuery ) -> None:
        await callback_query.answer()

        try:
            await BOT.delete_message( chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id )
        except:
            await BOT.send_message( chat_id=callback_query.message.chat.id, reply_to_message_id=callback_query.message.message_id, text="Ошибка: Не могу удалить сообщение" )
        
        try:
            user = await asyncio.wait_for( DB.getUser( callback_query.from_user.id ), 5 )
        except TimeoutError as e:
            return await BOT.send_message( chat_id=callback_query.message.chat.id, text="Ошибка соединения с БД. Попробуйте позднее" )

        if not user:
            logger.info('hashtags_save')
            logger.info(callback_query)
            return await BOT.send_message( chat_id=callback_query.message.chat.id, text="Ошибка: пользователь не найден, нажмите /start" )
        hashtags = callback_query.data.split('setup:hashtags:')[1]
        user.hashtags = hashtags
        try:
            user = await asyncio.wait_for( DB.saveUser(user), 5 )
        except TimeoutError as e:
            return await BOT.send_message( chat_id=callback_query.message.chat.id, text="Ошибка соединения с БД. Попробуйте позднее" )

        if not user.setuped:
            user.setuped = True
            try:
                user = await asyncio.wait_for( DB.saveUser(user), 5 )
            except TimeoutError as e:
                return await BOT.send_message( chat_id=callback_query.message.chat.id, text="Ошибка соединения с БД. Попробуйте позднее" )
        
            await BOT.send_message( chat_id=callback_query.message.chat.id, text="Настройка завершена" )
        else:
            return await BOT.send_message( chat_id=callback_query.message.chat.id, text="Формат хэштэгов: " + getattr(HashtagsModes,user.hashtags) )
        


    # renderers


    @staticmethod
    async def __setup_mode_start( chat_id: int, user_id: int ) -> None:
        try:
            user = await asyncio.wait_for( DB.getUser( user_id ), 5 )
        except TimeoutError as e:
            return await BOT.send_message( chat_id=chat_id, text="Ошибка соединения с БД. Попробуйте позднее" )
        if not user:
            return await BOT.send_message( chat_id=chat_id, text="Ошибка: пользователь не найден, нажмите /start" )

        text = "Выберите режим взаимодействия"
        image = os.path.join( os.path.dirname(__file__), '..','assets','bot_mode.jpg')

        builder = InlineKeyboardBuilder()
        builder.button( text=InteractionModes.inline, callback_data=f"setup:mode:inline" )
        if GC.bot_host:
            builder.button( text=InteractionModes.windowed, callback_data=f"setup:mode:windowed" )
        builder.adjust(1, repeat=True)

        await BOT.send_photo( chat_id=chat_id, photo=types.FSInputFile( image ), caption=text, reply_markup=builder.as_markup() )


    @staticmethod
    async def __setup_format_start( chat_id: int, user_id: int ) -> None:
        try:
            user = await asyncio.wait_for( DB.getUser( user_id ), 5 )
        except TimeoutError as e:
            return await BOT.send_message( chat_id=chat_id, text="Ошибка соединения с БД. Попробуйте позднее" )
        if not user:
            return await BOT.send_message( chat_id=chat_id, text="Ошибка: пользователь не найден, нажмите /start" )

        text = "Выберите формат (по умолчанию)"

        builder = InlineKeyboardBuilder()
        for format in GC.formats:
            builder.button( text=GC.formats[format], callback_data='setup:format:'+str(format))
        builder.adjust(1, repeat=True)

        await BOT.send_message( chat_id=chat_id, text=text, reply_markup=builder.as_markup() )


    @staticmethod
    async def __setup_cover_start( chat_id: int, user_id: int ) -> None:
        try:
            user = await asyncio.wait_for( DB.getUser( user_id ), 5 )
        except TimeoutError as e:
            return await BOT.send_message( chat_id=chat_id, text="Ошибка соединения с БД. Попробуйте позднее" )
        if not user:
            return await BOT.send_message( chat_id=chat_id, text="Ошибка: пользователь не найден, нажмите /start" )

        text = "Скачивать обложки отдельным файлом (по умолчанию)?"

        builder = InlineKeyboardBuilder()
        builder.button( text="Да", callback_data='setup:cover:yes')
        builder.button( text="Нет", callback_data='setup:cover:no')
        builder.adjust(1, repeat=True)

        await BOT.send_message( chat_id=chat_id, text=text, reply_markup=builder.as_markup() )


    @staticmethod
    async def __setup_images_start( chat_id: int, user_id: int ) -> None:
        try:
            user = await asyncio.wait_for( DB.getUser( user_id ), 5 )
        except TimeoutError as e:
            return await BOT.send_message( chat_id=chat_id, text="Ошибка соединения с БД. Попробуйте позднее" )
        if not user:
            return await BOT.send_message( chat_id=chat_id, text="Ошибка: пользователь не найден, нажмите /start" )

        text = "Скачивать изображения (по умолчанию)?"

        builder = InlineKeyboardBuilder()
        builder.button( text="Да", callback_data='setup:images:yes')
        builder.button( text="Нет", callback_data='setup:images:no')
        builder.adjust(1, repeat=True)

        await BOT.send_message( chat_id=chat_id, text=text, reply_markup=builder.as_markup() )


    @staticmethod
    async def __setup_hashtags_start( chat_id: int, user_id: int ) -> None:
        try:
            user = await asyncio.wait_for( DB.getUser( user_id ), 5 )
        except TimeoutError as e:
            return await BOT.send_message( chat_id=chat_id, text="Ошибка соединения с БД. Попробуйте позднее" )
        if not user:
            return await BOT.send_message( chat_id=chat_id, text="Ошибка: пользователь не найден, нажмите /start" )

        text = "Использовать хэштэги (по умолчанию)?"

        builder = InlineKeyboardBuilder()
        builder.button( text=HashtagsModes.no, callback_data='setup:hashtags:no')
        builder.button( text=HashtagsModes.bf, callback_data='setup:hashtags:bf')
        builder.button( text=HashtagsModes.gf, callback_data='setup:hashtags:gf')
        builder.adjust(1, repeat=True)

        await BOT.send_message( chat_id=chat_id, text=text, reply_markup=builder.as_markup() )