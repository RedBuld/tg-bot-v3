import os
import logging
import asyncio
from aiogram import Dispatcher, Router, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from app import models, variables
from app.configs import GC
from app.objects import DB, RD, BOT
from app.tools import clean_filename

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
        if user.setuped:
            builder.button( text="Да", callback_data=f"setup_global:start" )
        else:
            builder.button( text="Да", callback_data=f"setup_global:mode" )
        if user.setuped:
            builder.button( text="Нет", callback_data=f"setup_global:cancel" )
        builder.adjust(1, repeat=True)

        await BOT.send_message( chat_id=message.chat.id, text=text, parse_mode='HTML', reply_markup=builder.as_markup() )
    
    @staticmethod
    async def setup_command( message: types.Message ) -> None:

        text = "Что настроим?"

        builder = InlineKeyboardBuilder()
        builder.button( text="Режим взаимодействия", callback_data="setup_global:mode" )
        builder.button( text="Формат", callback_data="setup_global:format" )
        builder.button( text="Обложка", callback_data="setup_global:cover" )
        builder.button( text="Изображения", callback_data="setup_global:images" )
        builder.button( text="Хэштэги", callback_data="setup_global:hashtags" )
        builder.button( text="Название файла", callback_data="setup_global:filename" )
        builder.adjust(1, repeat=True)

        await BOT.send_message( chat_id=message.chat.id, text=text, reply_markup=builder.as_markup() )


    # callbacks


    @staticmethod
    async def setup_cancel( callback_query: types.CallbackQuery ) -> None:
        await callback_query.answer()

        try:
            await BOT.delete_message( chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id )
        except:
            pass


    @staticmethod
    async def setup_start( callback_query: types.CallbackQuery ) -> None:
        await callback_query.answer()

        try:
            await BOT.delete_message( chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id )
        except:
            pass
        
        await AccountSetupController.setup_command( callback_query.message )


    @staticmethod
    async def setup_mode( callback_query: types.CallbackQuery ) -> None:
        await callback_query.answer()

        try:
            await BOT.delete_message( chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id )
        except:
            pass
        
        try:
            user = await asyncio.wait_for( DB.getUser( callback_query.from_user.id ), 5 )
        except TimeoutError as e:
            return await BOT.send_message( chat_id=callback_query.message.chat.id, text="Ошибка соединения с БД. Попробуйте позднее" )
        if not user:
            return await BOT.send_message( chat_id=callback_query.message.chat.id, text="Ошибка: пользователь не найден, нажмите /start" )

        text = "Выберите режим взаимодействия"
        image = os.path.join( os.path.dirname(__file__), '..','..','assets','bot_mode.jpg')

        builder = InlineKeyboardBuilder()
        builder.button( text=variables.InteractionModes.inline, callback_data=f"setup_global:mode:inline" )
        if GC.bot_host:
            builder.button( text=variables.InteractionModes.windowed, callback_data=f"setup_global:mode:windowed" )
        builder.adjust(1, repeat=True)

        await BOT.send_photo( chat_id=callback_query.message.chat.id, photo=types.FSInputFile( image ), caption=text, reply_markup=builder.as_markup() )


    @staticmethod
    async def setup_format( callback_query: types.CallbackQuery ) -> None:
        await callback_query.answer()

        try:
            await BOT.delete_message( chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id )
        except Exception as e:
            pass

        try:
            user = await asyncio.wait_for( DB.getUser( callback_query.from_user.id ), 5 )
        except TimeoutError as e:
            return await BOT.send_message( chat_id=callback_query.message.chat.id, text="Ошибка соединения с БД. Попробуйте позднее" )
        if not user:
            return await BOT.send_message( chat_id=callback_query.message.chat.id, text="Ошибка: пользователь не найден, нажмите /start" )

        text = "Выберите формат (по умолчанию)"

        builder = InlineKeyboardBuilder()
        for format in GC.formats:
            builder.button( text=GC.formats[format], callback_data='setup_global:format:'+str(format))
        builder.adjust(1, repeat=True)

        await BOT.send_message( chat_id=callback_query.message.chat.id, text=text, reply_markup=builder.as_markup() )


    @staticmethod
    async def setup_cover( callback_query: types.CallbackQuery ) -> None:
        await callback_query.answer()

        try:
            await BOT.delete_message( chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id )
        except:
            pass
        
        try:
            user = await asyncio.wait_for( DB.getUser( callback_query.from_user.id ), 5 )
        except TimeoutError as e:
            return await BOT.send_message( chat_id=callback_query.message.chat.id, text="Ошибка соединения с БД. Попробуйте позднее" )
        if not user:
            return await BOT.send_message( chat_id=callback_query.message.chat.id, text="Ошибка: пользователь не найден, нажмите /start" )

        text = "Скачивать обложки отдельным файлом (по умолчанию)?"

        builder = InlineKeyboardBuilder()
        builder.button( text="Да", callback_data='setup_global:cover:yes')
        builder.button( text="Нет", callback_data='setup_global:cover:no')
        builder.adjust(1, repeat=True)

        await BOT.send_message( chat_id=callback_query.message.chat.id, text=text, reply_markup=builder.as_markup() )


    @staticmethod
    async def setup_images( callback_query: types.CallbackQuery ) -> None:
        await callback_query.answer()

        try:
            await BOT.delete_message( chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id )
        except:
            pass

        try:
            user = await asyncio.wait_for( DB.getUser( callback_query.from_user.id ), 5 )
        except TimeoutError as e:
            return await BOT.send_message( chat_id=callback_query.message.chat.id, text="Ошибка соединения с БД. Попробуйте позднее" )
        if not user:
            return await BOT.send_message( chat_id=callback_query.message.chat.id, text="Ошибка: пользователь не найден, нажмите /start" )

        text = "Скачивать изображения (по умолчанию)?"

        builder = InlineKeyboardBuilder()
        builder.button( text="Да", callback_data='setup_global:images:yes')
        builder.button( text="Нет", callback_data='setup_global:images:no')
        builder.adjust(1, repeat=True)

        await BOT.send_message( chat_id=callback_query.message.chat.id, text=text, reply_markup=builder.as_markup() )


    @staticmethod
    async def setup_hashtags( callback_query: types.CallbackQuery ) -> None:
        await callback_query.answer()

        try:
            await BOT.delete_message( chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id )
        except:
            pass
        
        try:
            user = await asyncio.wait_for( DB.getUser( callback_query.from_user.id ), 5 )
        except TimeoutError as e:
            return await BOT.send_message( chat_id=callback_query.message.chat.id, text="Ошибка соединения с БД. Попробуйте позднее" )
        if not user:
            return await BOT.send_message( chat_id=callback_query.message.chat.id, text="Ошибка: пользователь не найден, нажмите /start" )

        text = "Использовать хэштэги (по умолчанию)?"

        builder = InlineKeyboardBuilder()
        builder.button( text=variables.HashtagsModes.no, callback_data='setup_global:hashtags:no')
        builder.button( text=variables.HashtagsModes.bf, callback_data='setup_global:hashtags:bf')
        builder.button( text=variables.HashtagsModes.gf, callback_data='setup_global:hashtags:gf')
        builder.adjust(1, repeat=True)

        await BOT.send_message( chat_id=callback_query.message.chat.id, text=text, reply_markup=builder.as_markup() )


    @staticmethod
    async def setup_filename( callback_query: types.CallbackQuery, state: FSMContext ) -> None:
        await callback_query.answer()

        try:
            await BOT.delete_message( chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id )
        except:
            pass
        
        await state.set_state(variables.SetupAccountForm.filename)

        try:
            user = await asyncio.wait_for( DB.getUser( callback_query.from_user.id ), 5 )
        except TimeoutError as e:
            return await BOT.send_message( chat_id=callback_query.message.chat.id, text="Ошибка соединения с БД. Попробуйте позднее" )
        if not user:
            return await BOT.send_message( chat_id=callback_query.message.chat.id, text="Ошибка: пользователь не найден, нажмите /start" )

        text = "Отправьте параметры генерации названия файла\n\n`{Author.Name}` \\- автор\n`{Book.Title}` \\- название книги"
        if user.filename:
            text += f'\n\nТекущее: `{user.filename}`'
        text += f'\n\n_Выделенные фрагменты копируются при нажатии_'

        builder = InlineKeyboardBuilder()
        builder.button( text=f"Отмена", callback_data=f'setup_global:filename:cancel')
        builder.adjust(1, repeat=True)

        msg = await BOT.send_message( chat_id=callback_query.message.chat.id, text=text, reply_markup=builder.as_markup(), parse_mode="MarkdownV2" )
        await state.update_data(base_message=msg.message_id)


    # savers


    @staticmethod
    async def setup_mode_save( callback_query: types.CallbackQuery ) -> None:
        await callback_query.answer()

        try:
            await BOT.delete_message( chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id )
        except Exception as e:
            pass

        try:
            user = await asyncio.wait_for( DB.getUser( callback_query.from_user.id ), 5 )
        except TimeoutError as e:
            return await BOT.send_message( chat_id=callback_query.message.chat.id, text="Ошибка соединения с БД. Попробуйте позднее" )

        if not user:
            logger.info('mode_save')
            logger.info(callback_query)
            return await BOT.send_message( chat_id=callback_query.message.chat.id, text="Ошибка: пользователь не найден, нажмите /start" )

        _mode = callback_query.data.split('setup_global:mode:')[1]
        if _mode == 'inline':
            user.interact_mode = 0
        if _mode == 'windowed':
            user.interact_mode = 1

        try:
            user = await asyncio.wait_for( DB.saveUser(user), 5 )
        except TimeoutError as e:
            return await BOT.send_message( chat_id=callback_query.message.chat.id, text="Ошибка соединения с БД. Попробуйте позднее" )

        if not user:
            return await BOT.send_message( chat_id=callback_query.message.chat.id, text="Ошибка: пользователь не найден, нажмите /start" )
        
        if not user.setuped:
            await AccountSetupController.setup_format( callback_query )
        else:
            return await BOT.send_message( chat_id=callback_query.message.chat.id, text="Сохранен режим взаимодействия: " + getattr(variables.InteractionModes,_mode) )


    @staticmethod
    async def setup_format_save( callback_query: types.CallbackQuery ) -> None:
        await callback_query.answer()

        try:
            await BOT.delete_message( chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id )
        except Exception as e:
            pass
        
        try:
            user = await asyncio.wait_for( DB.getUser( callback_query.from_user.id ), 5 )
        except TimeoutError as e:
            return await BOT.send_message( chat_id=callback_query.message.chat.id, text="Ошибка соединения с БД. Попробуйте позднее" )

        if not user:
            return await BOT.send_message( chat_id=callback_query.message.chat.id, text="Ошибка: пользователь не найден, нажмите /start" )

        user.format = callback_query.data.split('setup_global:format:')[1]
        try:
            user = await asyncio.wait_for( DB.saveUser(user), 5 )
        except TimeoutError as e:
            return await BOT.send_message( chat_id=callback_query.message.chat.id, text="Ошибка соединения с БД. Попробуйте позднее" )

        if not user.setuped:
            await AccountSetupController.setup_cover( callback_query )
        else:
            return await BOT.send_message( chat_id=callback_query.message.chat.id, text="Сохранен формат по умолчанию: " + user.format )


    @staticmethod
    async def setup_cover_save( callback_query: types.CallbackQuery ) -> None:
        await callback_query.answer()

        try:
            await BOT.delete_message( chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id )
        except:
            pass
        
        try:
            user = await asyncio.wait_for( DB.getUser( callback_query.from_user.id ), 5 )
        except TimeoutError as e:
            return await BOT.send_message( chat_id=callback_query.message.chat.id, text="Ошибка соединения с БД. Попробуйте позднее" )

        if not user:
            logger.info('cover_save')
            logger.info(callback_query)
            return await BOT.send_message( chat_id=callback_query.message.chat.id, text="Ошибка: пользователь не найден, нажмите /start" )

        _cover = callback_query.data.split('setup_global:cover:')[1]
        if _cover == 'yes':
            user.cover = True
        if _cover == 'no':
            user.cover = False

        try:
            user = await asyncio.wait_for( DB.saveUser(user), 5 )
        except TimeoutError as e:
            return await BOT.send_message( chat_id=callback_query.message.chat.id, text="Ошибка соединения с БД. Попробуйте позднее" )

        if not user.setuped:
            await AccountSetupController.setup_images( callback_query )
        else:
            return await BOT.send_message( chat_id=callback_query.message.chat.id, text="Скачивание обложек по умолчанию: " + ('Да' if user.cover else 'Нет') )


    @staticmethod
    async def setup_images_save( callback_query: types.CallbackQuery ) -> None:
        await callback_query.answer()

        try:
            await BOT.delete_message( chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id )
        except:
            pass
        
        try:
            user = await asyncio.wait_for( DB.getUser( callback_query.from_user.id ), 5 )
        except TimeoutError as e:
            return await BOT.send_message( chat_id=callback_query.message.chat.id, text="Ошибка соединения с БД. Попробуйте позднее" )

        if not user:
            return await BOT.send_message( chat_id=callback_query.message.chat.id, text="Ошибка: пользователь не найден, нажмите /start" )

        _images = callback_query.data.split('setup_global:images:')[1]
        if _images == 'yes':
            user.images = True
        if _images == 'no':
            user.images = False

        try:
            user = await asyncio.wait_for( DB.saveUser(user), 5 )
        except TimeoutError as e:
            return await BOT.send_message( chat_id=callback_query.message.chat.id, text="Ошибка соединения с БД. Попробуйте позднее" )

        if not user.setuped:
            await AccountSetupController.setup_hashtags( callback_query )
        else:
            return await BOT.send_message( chat_id=callback_query.message.chat.id, text="Скачивание изображений по умолчанию: " + ('Да' if user.images else 'Нет') )


    @staticmethod
    async def setup_hashtags_save( callback_query: types.CallbackQuery ) -> None:
        await callback_query.answer()

        try:
            await BOT.delete_message( chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id )
        except:
            pass
        
        try:
            user = await asyncio.wait_for( DB.getUser( callback_query.from_user.id ), 5 )
        except TimeoutError as e:
            return await BOT.send_message( chat_id=callback_query.message.chat.id, text="Ошибка соединения с БД. Попробуйте позднее" )

        if not user:
            return await BOT.send_message( chat_id=callback_query.message.chat.id, text="Ошибка: пользователь не найден, нажмите /start" )

        hashtags = callback_query.data.split('setup_global:hashtags:')[1]
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
            return await BOT.send_message( chat_id=callback_query.message.chat.id, text="Формат хэштэгов: " + getattr(variables.HashtagsModes,user.hashtags) )


    @staticmethod
    async def setup_filename_save( message: types.Message, state: FSMContext ) -> None:

        _filename = clean_filename( message.text.strip() )

        sf_data = await state.get_data()

        await state.clear()

        try:
            await BOT.delete_message( chat_id=message.chat.id, message_id=message.message_id )
        except:
            pass

        try:
            await BOT.delete_message( chat_id=message.chat.id, message_id=sf_data['base_message'] )
        except:
            pass
        
        try:
            user = await asyncio.wait_for( DB.getUser( message.from_user.id ), 5 )
        except TimeoutError as e:
            return await BOT.send_message( chat_id=message.chat.id, text="Ошибка соединения с БД. Попробуйте позднее" )

        if not user:
            return await BOT.send_message( chat_id=message.chat.id, text="Ошибка: пользователь не найден, нажмите /start" )

        try:
            await BOT.delete_message( chat_id=message.chat.id, message_id=message.message_id )
        except:
            pass

        user.filename = _filename

        try:
            user = await asyncio.wait_for( DB.saveUser(user), 5 )
        except TimeoutError as e:
            return await BOT.send_message( chat_id=message.chat.id, text="Ошибка соединения с БД. Попробуйте позднее" )

        return await BOT.send_message( chat_id=message.chat.id, text=f"Параметры генерации названия файла: `{_filename}`", parse_mode='MarkdownV2' )


    @staticmethod
    async def setup_filename_save_cb( callback_query: types.CallbackQuery, state: FSMContext ) -> None:
        await callback_query.answer()

        await state.clear()

        _filename = callback_query.data.split('setup_global:filename:')[1]

        try:
            await BOT.delete_message( chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id )
        except:
            pass
        
        try:
            user = await asyncio.wait_for( DB.getUser( callback_query.from_user.id ), 5 )
        except TimeoutError as e:
            return await BOT.send_message( chat_id=callback_query.message.chat.id, text="Ошибка соединения с БД. Попробуйте позднее" )

        if not user:
            return await BOT.send_message( chat_id=callback_query.message.chat.id, text="Ошибка: пользователь не найден, нажмите /start" )

        if _filename == 'default':
            user.filename = None
            _filename = 'По умолчанию'
        else:
            return

        try:
            user = await asyncio.wait_for( DB.saveUser(user), 5 )
        except TimeoutError as e:
            return await BOT.send_message( chat_id=callback_query.message.chat.id, text="Ошибка соединения с БД. Попробуйте позднее" )

        return await BOT.send_message( chat_id=callback_query.message.chat.id, text=f"Параметры генерации названия файла: `{_filename}`", parse_mode='MarkdownV2' )