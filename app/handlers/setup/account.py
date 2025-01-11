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
from app.tools import cleanFilename

logger = logging.getLogger( __name__ )

class AccountSetupController:

    @staticmethod
    async def Start( message: types.Message ) -> None:

        if message.from_user.is_bot != False:
            return

        try:
            user = await asyncio.wait_for( DB.GetUser( message.from_user.id ), 5 )
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
                user = await asyncio.wait_for( DB.SaveUser(user), 5 )
            except TimeoutError as e:
                return await BOT.send_message( chat_id=message.chat.id, text="Ошибка соединения с БД. Попробуйте позднее" )
        
        try:
            user = await asyncio.wait_for( DB.GetUser( message.from_user.id ), 5 )
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
    async def SelectOption( message: types.Message ) -> None:

        text = "Что настроим?"

        builder = InlineKeyboardBuilder()
        builder.button( text="Режим взаимодействия", callback_data="setup_global:mode" )
        builder.button( text="Формат", callback_data="setup_global:format" )
        builder.button( text="Обложка", callback_data="setup_global:cover" )
        builder.button( text="Превью", callback_data="setup_global:thumb" )
        builder.button( text="Изображения", callback_data="setup_global:images" )
        builder.button( text="Хэштэги", callback_data="setup_global:hashtags" )
        builder.button( text="Название файла", callback_data="setup_global:filename" )
        builder.adjust(1, repeat=True)

        await BOT.send_message( chat_id=message.chat.id, text=text, reply_markup=builder.as_markup() )


    # callbacks


    @staticmethod
    async def StartSetup( callback_query: types.CallbackQuery ) -> None:
        await callback_query.answer()

        try:
            await BOT.delete_message( chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id )
        except:
            pass
        
        await AccountSetupController.SelectOption( callback_query.message )


    @staticmethod
    async def CancelSetup( callback_query: types.CallbackQuery ) -> None:
        await callback_query.answer()

        try:
            await BOT.delete_message( chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id )
        except:
            pass


    ##
    ## INTERACTION MODE
    ##


    @staticmethod
    async def SelectMode( callback_query: types.CallbackQuery ) -> None:
        await callback_query.answer()

        try:
            await BOT.delete_message( chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id )
        except:
            pass
        
        try:
            user = await asyncio.wait_for( DB.GetUser( callback_query.from_user.id ), 5 )
        except TimeoutError as e:
            return await BOT.send_message( chat_id=callback_query.message.chat.id, text="Ошибка соединения с БД. Попробуйте позднее" )
        if not user:
            return await BOT.send_message( chat_id=callback_query.message.chat.id, text="Ошибка: пользователь не найден, нажмите /start" )

        text = "Выберите режим взаимодействия"
        image = os.path.join( os.path.dirname(__file__), '..','..','assets','bot_mode.jpg')

        builder = InlineKeyboardBuilder()
        builder.button( text=variables.InteractionModes.inline, callback_data=f"setup_global:mode:inline" )
        if GC.url:
            builder.button( text=variables.InteractionModes.windowed, callback_data=f"setup_global:mode:windowed" )
        builder.adjust(1, repeat=True)

        await BOT.send_photo( chat_id=callback_query.message.chat.id, photo=types.FSInputFile( image ), caption=text, reply_markup=builder.as_markup() )


    @staticmethod
    async def SaveMode( callback_query: types.CallbackQuery ) -> None:
        await callback_query.answer()

        try:
            await BOT.delete_message( chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id )
        except Exception as e:
            pass

        try:
            user = await asyncio.wait_for( DB.GetUser( callback_query.from_user.id ), 5 )
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
            user = await asyncio.wait_for( DB.SaveUser(user), 5 )
        except TimeoutError as e:
            return await BOT.send_message( chat_id=callback_query.message.chat.id, text="Ошибка соединения с БД. Попробуйте позднее" )

        if not user:
            return await BOT.send_message( chat_id=callback_query.message.chat.id, text="Ошибка: пользователь не найден, нажмите /start" )
        
        if not user.setuped:
            await AccountSetupController.SelectFormat( callback_query )
        else:
            return await BOT.send_message( chat_id=callback_query.message.chat.id, text="Сохранен режим взаимодействия: " + getattr(variables.InteractionModes,_mode) )


    ##
    ## FORMAT
    ##


    @staticmethod
    async def SelectFormat( callback_query: types.CallbackQuery ) -> None:
        await callback_query.answer()

        try:
            await BOT.delete_message( chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id )
        except Exception as e:
            pass

        try:
            user = await asyncio.wait_for( DB.GetUser( callback_query.from_user.id ), 5 )
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
    async def SaveFormat( callback_query: types.CallbackQuery ) -> None:
        await callback_query.answer()

        try:
            await BOT.delete_message( chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id )
        except Exception as e:
            pass
        
        try:
            user = await asyncio.wait_for( DB.GetUser( callback_query.from_user.id ), 5 )
        except TimeoutError as e:
            return await BOT.send_message( chat_id=callback_query.message.chat.id, text="Ошибка соединения с БД. Попробуйте позднее" )

        if not user:
            return await BOT.send_message( chat_id=callback_query.message.chat.id, text="Ошибка: пользователь не найден, нажмите /start" )

        user.format = callback_query.data.split('setup_global:format:')[1]
        try:
            user = await asyncio.wait_for( DB.SaveUser(user), 5 )
        except TimeoutError as e:
            return await BOT.send_message( chat_id=callback_query.message.chat.id, text="Ошибка соединения с БД. Попробуйте позднее" )

        if not user.setuped:
            await AccountSetupController.SelectCover( callback_query )
        else:
            return await BOT.send_message( chat_id=callback_query.message.chat.id, text="Сохранен формат по умолчанию: " + user.format )


    ##
    ## COVER
    ##


    @staticmethod
    async def SelectCover( callback_query: types.CallbackQuery ) -> None:
        await callback_query.answer()

        try:
            await BOT.delete_message( chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id )
        except:
            pass
        
        try:
            user = await asyncio.wait_for( DB.GetUser( callback_query.from_user.id ), 5 )
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
    async def SaveCover( callback_query: types.CallbackQuery ) -> None:
        await callback_query.answer()

        try:
            await BOT.delete_message( chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id )
        except:
            pass
        
        try:
            user = await asyncio.wait_for( DB.GetUser( callback_query.from_user.id ), 5 )
        except TimeoutError as e:
            return await BOT.send_message( chat_id=callback_query.message.chat.id, text="Ошибка соединения с БД. Попробуйте позднее" )

        if not user:
            return await BOT.send_message( chat_id=callback_query.message.chat.id, text="Ошибка: пользователь не найден, нажмите /start" )

        _cover = callback_query.data.split('setup_global:cover:')[1]
        if _cover == 'yes':
            user.cover = True
        if _cover == 'no':
            user.cover = False

        try:
            user = await asyncio.wait_for( DB.SaveUser(user), 5 )
        except TimeoutError as e:
            return await BOT.send_message( chat_id=callback_query.message.chat.id, text="Ошибка соединения с БД. Попробуйте позднее" )

        if not user.setuped:
            await AccountSetupController.SelectThumbnail( callback_query )
        else:
            return await BOT.send_message( chat_id=callback_query.message.chat.id, text="Скачивание обложек по умолчанию: " + ('Да' if user.cover else 'Нет') )


    ##
    ## THUMBNAIL
    ##


    @staticmethod
    async def SelectThumbnail( callback_query: types.CallbackQuery ) -> None:
        await callback_query.answer()

        try:
            await BOT.delete_message( chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id )
        except:
            pass
        
        try:
            user = await asyncio.wait_for( DB.GetUser( callback_query.from_user.id ), 5 )
        except TimeoutError as e:
            return await BOT.send_message( chat_id=callback_query.message.chat.id, text="Ошибка соединения с БД. Попробуйте позднее" )
        if not user:
            return await BOT.send_message( chat_id=callback_query.message.chat.id, text="Ошибка: пользователь не найден, нажмите /start" )

        text = "Добавлять превью ТГ (по умолчанию)?"

        builder = InlineKeyboardBuilder()
        builder.button( text="Да", callback_data='setup_global:thumb:yes')
        builder.button( text="Нет", callback_data='setup_global:thumb:no')
        builder.adjust(1, repeat=True)

        await BOT.send_message( chat_id=callback_query.message.chat.id, text=text, reply_markup=builder.as_markup() )


    @staticmethod
    async def SaveThumbnail( callback_query: types.CallbackQuery ) -> None:
        await callback_query.answer()

        try:
            await BOT.delete_message( chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id )
        except:
            pass
        
        try:
            user = await asyncio.wait_for( DB.GetUser( callback_query.from_user.id ), 5 )
        except TimeoutError as e:
            return await BOT.send_message( chat_id=callback_query.message.chat.id, text="Ошибка соединения с БД. Попробуйте позднее" )

        if not user:
            return await BOT.send_message( chat_id=callback_query.message.chat.id, text="Ошибка: пользователь не найден, нажмите /start" )

        _thumb = callback_query.data.split('setup_global:thumb:')[1]
        if _thumb == 'yes':
            user.thumb = True
        if _thumb == 'no':
            user.thumb = False

        try:
            user = await asyncio.wait_for( DB.SaveUser(user), 5 )
        except TimeoutError as e:
            return await BOT.send_message( chat_id=callback_query.message.chat.id, text="Ошибка соединения с БД. Попробуйте позднее" )

        if not user.setuped:
            await AccountSetupController.SelectImages( callback_query )
        else:
            return await BOT.send_message( chat_id=callback_query.message.chat.id, text="Добавлять превью ТГ по умолчанию: " + ('Да' if user.thumb else 'Нет') )


    ##
    ## IMAGES
    ##


    @staticmethod
    async def SelectImages( callback_query: types.CallbackQuery ) -> None:
        await callback_query.answer()

        try:
            await BOT.delete_message( chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id )
        except:
            pass

        try:
            user = await asyncio.wait_for( DB.GetUser( callback_query.from_user.id ), 5 )
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
    async def SaveImages( callback_query: types.CallbackQuery ) -> None:
        await callback_query.answer()

        try:
            await BOT.delete_message( chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id )
        except:
            pass
        
        try:
            user = await asyncio.wait_for( DB.GetUser( callback_query.from_user.id ), 5 )
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
            user = await asyncio.wait_for( DB.SaveUser(user), 5 )
        except TimeoutError as e:
            return await BOT.send_message( chat_id=callback_query.message.chat.id, text="Ошибка соединения с БД. Попробуйте позднее" )

        if not user.setuped:
            await AccountSetupController.SelectHashtags( callback_query )
        else:
            return await BOT.send_message( chat_id=callback_query.message.chat.id, text="Скачивание изображений по умолчанию: " + ('Да' if user.images else 'Нет') )


    ##
    ##
    ##


    @staticmethod
    async def SelectHashtags( callback_query: types.CallbackQuery ) -> None:
        await callback_query.answer()

        try:
            await BOT.delete_message( chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id )
        except:
            pass
        
        try:
            user = await asyncio.wait_for( DB.GetUser( callback_query.from_user.id ), 5 )
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
    async def SaveHashtags( callback_query: types.CallbackQuery ) -> None:
        await callback_query.answer()

        try:
            await BOT.delete_message( chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id )
        except:
            pass
        
        try:
            user = await asyncio.wait_for( DB.GetUser( callback_query.from_user.id ), 5 )
        except TimeoutError as e:
            return await BOT.send_message( chat_id=callback_query.message.chat.id, text="Ошибка соединения с БД. Попробуйте позднее" )

        if not user:
            return await BOT.send_message( chat_id=callback_query.message.chat.id, text="Ошибка: пользователь не найден, нажмите /start" )

        hashtags = callback_query.data.split('setup_global:hashtags:')[1]
        user.hashtags = hashtags
        try:
            user = await asyncio.wait_for( DB.SaveUser(user), 5 )
        except TimeoutError as e:
            return await BOT.send_message( chat_id=callback_query.message.chat.id, text="Ошибка соединения с БД. Попробуйте позднее" )

        if not user.setuped:
            user.setuped = True
            try:
                user = await asyncio.wait_for( DB.SaveUser(user), 5 )
            except TimeoutError as e:
                return await BOT.send_message( chat_id=callback_query.message.chat.id, text="Ошибка соединения с БД. Попробуйте позднее" )
        
            await BOT.send_message( chat_id=callback_query.message.chat.id, text="Настройка завершена" )
            await BOT.send_message( chat_id=callback_query.message.chat.id, text="Обо всех ошибках / зависаниях сообщайте в https://t.me/elib_fb2_bot_support" )
        else:
            return await BOT.send_message( chat_id=callback_query.message.chat.id, text="Формат хэштэгов: " + getattr(variables.HashtagsModes,user.hashtags) )


    ##
    ## FILENAME
    ##


    @staticmethod
    async def SetupFilename( callback_query: types.CallbackQuery, state: FSMContext ) -> None:
        await callback_query.answer()

        try:
            await BOT.delete_message( chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id )
        except:
            pass
        
        await state.set_state(variables.SetupAccountForm.filename)

        try:
            user = await asyncio.wait_for( DB.GetUser( callback_query.from_user.id ), 5 )
        except TimeoutError as e:
            return await BOT.send_message( chat_id=callback_query.message.chat.id, text="Ошибка соединения с БД. Попробуйте позднее" )
        if not user:
            return await BOT.send_message( chat_id=callback_query.message.chat.id, text="Ошибка: пользователь не найден, нажмите /start" )

        text = "Отправьте параметры генерации названия файла\n\n`{Author.Name}` \\- автор\n`{Book.Title}` \\- название книги\n`{:if,Seria.HasSeria} \\- {Seria.Name} #{Seria.Number}{:ifend}` \\- серия с номером"
        if user.filename:
            text += f'\n\nТекущее: `{user.filename}`'
        text += '\n\n_Выделенные фрагменты копируются при нажатии_\n_можно использовать несколько элементов сразу_'
        text += '\n\n`{Author.Name} \\- {Book.Title}`'
        text += '\n`{Author.Name}{:if,Seria.HasSeria} \\- {Seria.Name} #{Seria.Number}{:ifend} \\- {Book.Title}`'

        builder = InlineKeyboardBuilder()
        builder.button( text=f"По умолчанию", callback_data=f'setup_global:filename:default')
        builder.button( text=f"Отмена", callback_data=f'setup_global:filename:cancel')
        builder.adjust(1, repeat=True)

        msg = await BOT.send_message( chat_id=callback_query.message.chat.id, text=text, reply_markup=builder.as_markup(), parse_mode="MarkdownV2" )
        await state.update_data(base_message=msg.message_id)


    @staticmethod
    async def SaveFilename( message: types.Message, state: FSMContext ) -> None:

        _filename = cleanFilename( message.text.strip() )

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
            user = await asyncio.wait_for( DB.GetUser( message.from_user.id ), 5 )
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
            user = await asyncio.wait_for( DB.SaveUser(user), 5 )
        except TimeoutError as e:
            return await BOT.send_message( chat_id=message.chat.id, text="Ошибка соединения с БД. Попробуйте позднее" )

        return await BOT.send_message( chat_id=message.chat.id, text=f"Параметры генерации названия файла: `{_filename}`", parse_mode='MarkdownV2' )


    @staticmethod
    async def SaveFilenameCallback( callback_query: types.CallbackQuery, state: FSMContext ) -> None:
        await callback_query.answer()

        await state.clear()

        _filename = callback_query.data.split('setup_global:filename:')[1]

        try:
            await BOT.delete_message( chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id )
        except:
            pass
        
        try:
            user = await asyncio.wait_for( DB.GetUser( callback_query.from_user.id ), 5 )
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
            user = await asyncio.wait_for( DB.SaveUser(user), 5 )
        except TimeoutError as e:
            return await BOT.send_message( chat_id=callback_query.message.chat.id, text="Ошибка соединения с БД. Попробуйте позднее" )

        return await BOT.send_message( chat_id=callback_query.message.chat.id, text=f"Параметры генерации названия файла: `{_filename}`", parse_mode='MarkdownV2' )