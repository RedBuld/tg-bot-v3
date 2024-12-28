import idna
import logging
import asyncio
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from app import models, variables
from app.configs import GC
from app.objects import DB, RD, BOT
from app.tools import yesOrNo
from app.tools import cleanFilename
from app.classes.interconnect import Interconnect

logger = logging.getLogger( __name__ )

class SitesSetupController:

    @staticmethod
    async def SelectSite( message: types.Message ) -> None:
        
        sites_list = await Interconnect.GetSitesActive()

        builder = InlineKeyboardBuilder()

        for site in sites_list:
            builder.button( text=idna.decode(site), callback_data=f"setup_sites:select_site:{site}" )

        builder.adjust( 1, repeat=True )

        await BOT.send_message( chat_id=message.chat.id, text="Выберите сайт", reply_markup=builder.as_markup() )


    @staticmethod
    async def StartSetup( callback_query: types.CallbackQuery ) -> None:
        await callback_query.answer()

        site = callback_query.data.split('setup_sites:select_site:')[1]
        
        await SitesSetupController.renderMenu( callback_query.message.chat.id, callback_query.message.message_id, site )


    @staticmethod
    async def CancelSetup( callback_query: types.CallbackQuery ) -> None:
        await callback_query.answer()

        try:
            await BOT.delete_message( chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id )
        except:
            await BOT.send_message( chat_id=callback_query.message.chat.id, reply_to_message_id=callback_query.message.message_id, text="Ошибка: Не могу удалить сообщение" )


    @staticmethod
    async def ResetSiteConfig( callback_query: types.CallbackQuery ) -> None:
        await callback_query.answer()

        site = callback_query.data.split('setup_sites:reset:')[1]

        try:
            await asyncio.wait_for( DB.deleteSiteConfig( callback_query.from_user.id, site ), 5 )
        except TimeoutError as e:
            return await BOT.send_message( chat_id=callback_query.message.chat.id, text="Ошибка соединения с БД. Попробуйте позднее" )

        try:
            await BOT.delete_message( chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id )
        except:
            await BOT.send_message( chat_id=callback_query.message.chat.id, reply_to_message_id=callback_query.message.message_id, text="Ошибка: Не могу удалить сообщение" )


    ##
    ## AUTH
    ##


    @staticmethod
    async def SelectAuth( callback_query: types.CallbackQuery ) -> None:
        await callback_query.answer()

        site = callback_query.data.split('setup_sites:select_auth:')[1]

        text = "Выберите доступы"

        site_config = await SitesSetupController.getConfig( callback_query.from_user.id, site )

        demo_login = True if site in GC.demo else False
        uas = await DB.GetUserAuthsForSite( user_id=callback_query.from_user.id, site=site )

        builder = InlineKeyboardBuilder()
        builder.button( text=f'{yesOrNo(site_config.auth, None)} По умолчанию', callback_data=f'setup_sites:save_auth:{site}:default')
        for ua in uas:
            ua_name = ua.get_name()
            builder.button( text=f'{yesOrNo(site_config.auth, str(ua.id))} {ua_name}', callback_data=f'setup_sites:save_auth:{site}:'+str(ua.id))
        if demo_login:
            builder.button( text=f'{yesOrNo(site_config.auth, 'anon')} Анонимные доступы', callback_data=f'setup_sites:save_auth:{site}:anon')
        builder.adjust( 1, repeat=True )

        await BOT.edit_message_text( chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id, text=text, reply_markup=builder.as_markup() )


    @staticmethod
    async def SaveAuth( callback_query: types.CallbackQuery ) -> None:
        await callback_query.answer()

        data = callback_query.data.split('setup_sites:save_auth:')[1]
        site, _auth = data.split(':')
        
        site_config = await SitesSetupController.getConfig( user_id=callback_query.from_user.id, site=site )

        if not site_config:
            return await BOT.send_message( chat_id=callback_query.message.chat.id, text="Ошибка соединения с БД. Попробуйте позднее" )

        if _auth == 'default':
            site_config.auth = None
        else:
            site_config.auth = _auth

        try:
            site_config = await asyncio.wait_for( DB.SaveSiteConfig( site_config ), 5 )
        except TimeoutError as e:
            return await BOT.send_message( chat_id=callback_query.message.chat.id, text="Ошибка соединения с БД. Попробуйте позднее" )

        await SitesSetupController.renderMenu( callback_query.message.chat.id, callback_query.message.message_id, site )


    ##
    ## FORMAT
    ##


    @staticmethod
    async def SelectFormat( callback_query: types.CallbackQuery ) -> None:
        await callback_query.answer()

        site = callback_query.data.split('setup_sites:select_format:')[1]

        text = "Выберите формат"

        site_data = await Interconnect.GetSiteData( site )
        site_config = await SitesSetupController.getConfig( callback_query.from_user.id, site )

        builder = InlineKeyboardBuilder()
        builder.button( text=f'{yesOrNo(site_config.format, None)} По умолчанию', callback_data=f'setup_sites:save_format:{site}:default')
        for site_format in site_data.formats:
            if site_format in GC.formats:
                builder.button( text=f'{yesOrNo(site_config.format, site_format)} {GC.formats[site_format]}', callback_data=f'setup_sites:save_format:{site}:'+site_format)
        builder.adjust( 1, repeat=True )

        await BOT.edit_message_text( chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id, text=text, reply_markup=builder.as_markup() )


    @staticmethod
    async def SaveFormat( callback_query: types.CallbackQuery ) -> None:
        await callback_query.answer()

        data = callback_query.data.split('setup_sites:save_format:')[1]
        site, _format = data.split(':')
        
        site_config = await SitesSetupController.getConfig( user_id=callback_query.from_user.id, site=site )

        if not site_config:
            return await BOT.send_message( chat_id=callback_query.message.chat.id, text="Ошибка соединения с БД. Попробуйте позднее" )

        if _format == 'default':
            site_config.format = None
        else:
            site_config.format = _format

        try:
            site_config = await asyncio.wait_for( DB.SaveSiteConfig( site_config ), 5 )
        except TimeoutError as e:
            return await BOT.send_message( chat_id=callback_query.message.chat.id, text="Ошибка соединения с БД. Попробуйте позднее" )

        await SitesSetupController.renderMenu( callback_query.message.chat.id, callback_query.message.message_id, site )


    ##
    ## COVER
    ##


    @staticmethod
    async def SelectCover( callback_query: types.CallbackQuery ) -> None:
        await callback_query.answer()

        site = callback_query.data.split('setup_sites:select_cover:')[1]

        site_config = await SitesSetupController.getConfig( callback_query.from_user.id, site )

        text = "Скачивать обложки отдельным файлом?"

        builder = InlineKeyboardBuilder()
        builder.button( text=f"{yesOrNo(site_config.cover,None)} По умолчанию", callback_data=f'setup_sites:save_cover:{site}:default')
        builder.button( text=f"{yesOrNo(site_config.cover,True)} Да", callback_data=f'setup_sites:save_cover:{site}:yes')
        builder.button( text=f"{yesOrNo(site_config.cover,False)} Нет", callback_data=f'setup_sites:save_cover:{site}:no')
        builder.adjust( 1, repeat=True )

        await BOT.edit_message_text( chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id, text=text, reply_markup=builder.as_markup() )


    @staticmethod
    async def SaveCover( callback_query: types.CallbackQuery ) -> None:
        await callback_query.answer()

        data = callback_query.data.split('setup_sites:save_cover:')[1]
        site, _cover = data.split(':')
        
        site_config = await SitesSetupController.getConfig( user_id=callback_query.from_user.id, site=site )

        if not site_config:
            return await BOT.send_message( chat_id=callback_query.message.chat.id, text="Ошибка соединения с БД. Попробуйте позднее" )

        if _cover == 'default':
            site_config.cover = None
        elif _cover == 'yes':
            site_config.cover = True
        elif _cover == 'no':
            site_config.cover = False

        try:
            site_config = await asyncio.wait_for( DB.SaveSiteConfig( site_config ), 5 )
        except TimeoutError as e:
            return await BOT.send_message( chat_id=callback_query.message.chat.id, text="Ошибка соединения с БД. Попробуйте позднее" )

        await SitesSetupController.renderMenu( callback_query.message.chat.id, callback_query.message.message_id, site )


    ##
    ## IMAGES
    ##


    @staticmethod
    async def SelectImages( callback_query: types.CallbackQuery ) -> None:
        await callback_query.answer()

        site = callback_query.data.split('setup_sites:select_images:')[1]

        site_config = await SitesSetupController.getConfig( callback_query.from_user.id, site )

        text = "Скачивать изображения?"

        builder = InlineKeyboardBuilder()
        builder.button( text=f"{yesOrNo(site_config.images,None)} По умолчанию", callback_data=f'setup_sites:save_images:{site}:default')
        builder.button( text=f"{yesOrNo(site_config.images,True)} Да", callback_data=f'setup_sites:save_images:{site}:yes')
        builder.button( text=f"{yesOrNo(site_config.images,False)} Нет", callback_data=f'setup_sites:save_images:{site}:no')
        builder.adjust( 1, repeat=True )

        await BOT.edit_message_text( chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id, text=text, reply_markup=builder.as_markup() )


    @staticmethod
    async def SaveImages( callback_query: types.CallbackQuery ) -> None:
        await callback_query.answer()

        data = callback_query.data.split('setup_sites:save_images:')[1]
        site, _images = data.split(':')
        
        site_config = await SitesSetupController.getConfig( user_id=callback_query.from_user.id, site=site )

        if not site_config:
            return await BOT.send_message( chat_id=callback_query.message.chat.id, text="Ошибка соединения с БД. Попробуйте позднее" )

        if _images == 'default':
            site_config.images = None
        elif _images == 'yes':
            site_config.images = True
        elif _images == 'no':
            site_config.images = False

        try:
            site_config = await asyncio.wait_for( DB.SaveSiteConfig( site_config ), 5 )
        except TimeoutError as e:
            return await BOT.send_message( chat_id=callback_query.message.chat.id, text="Ошибка соединения с БД. Попробуйте позднее" )

        await SitesSetupController.renderMenu( callback_query.message.chat.id, callback_query.message.message_id, site )


    ##
    ## HASHTAGS
    ##


    @staticmethod
    async def SelectHashtags( callback_query: types.CallbackQuery ) -> None:
        await callback_query.answer()

        site = callback_query.data.split('setup_sites:select_hashtags:')[1]

        site_config = await SitesSetupController.getConfig( callback_query.from_user.id, site )

        text = "Использовать хэштэги?"

        builder = InlineKeyboardBuilder()
        builder.button( text=f"{yesOrNo(site_config.hashtags,None)} По умолчанию", callback_data=f'setup_sites:save_hashtags:{site}:default')
        builder.button( text=f"{yesOrNo(site_config.hashtags,'no')} {variables.HashtagsModes.no}", callback_data=f'setup_sites:save_hashtags:{site}:no')
        builder.button( text=f"{yesOrNo(site_config.hashtags,'bf')} {variables.HashtagsModes.bf}", callback_data=f'setup_sites:save_hashtags:{site}:bf')
        builder.button( text=f"{yesOrNo(site_config.hashtags,'gf')} {variables.HashtagsModes.gf}", callback_data=f'setup_sites:save_hashtags:{site}:gf')
        builder.adjust( 1, repeat=True )

        await BOT.edit_message_text( chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id, text=text, reply_markup=builder.as_markup() )


    @staticmethod
    async def SaveHashtags( callback_query: types.CallbackQuery ) -> None:
        await callback_query.answer()

        data = callback_query.data.split('setup_sites:save_hashtags:')[1]
        site, _hashtags = data.split(':')
        
        site_config = await SitesSetupController.getConfig( user_id=callback_query.from_user.id, site=site )

        if not site_config:
            return await BOT.send_message( chat_id=callback_query.message.chat.id, text="Ошибка соединения с БД. Попробуйте позднее" )

        if _hashtags == 'default':
            site_config.hashtags = None
        else:
            site_config.hashtags = _hashtags

        try:
            site_config = await asyncio.wait_for( DB.SaveSiteConfig( site_config ), 5 )
        except TimeoutError as e:
            return await BOT.send_message( chat_id=callback_query.message.chat.id, text="Ошибка соединения с БД. Попробуйте позднее" )

        await SitesSetupController.renderMenu( callback_query.message.chat.id, callback_query.message.message_id, site )


    ##
    ## FILENAME
    ##


    @staticmethod
    async def SetupFilename( callback_query: types.CallbackQuery, state: FSMContext ) -> None:
        await callback_query.answer()

        site = callback_query.data.split('setup_sites:setup_filename:')[1]

        await state.set_state( variables.SetupSiteForm.filename )
        await state.update_data( site=site )
        await state.update_data( base_message=callback_query.message.message_id )

        site_config = await SitesSetupController.getConfig( callback_query.from_user.id, site )

        text = "Отправьте параметры генерации названия файла\n\n`{Author.Name}` \\- автор\n`{Book.Title}` \\- название книги\n`{:if,Seria.HasSeria} - {Seria.Name} #{Seria.Number}{:ifend}` \\- серия с номером"
        if site_config.filename:
            text += f'\n\nТекущее: `{site_config.filename}`'
        text += '\n\n_Выделенные фрагменты копируются при нажатии_\n_можно использовать несколько элементов сразу_'
        text += '\n\n`{Author.Name} \\- {Book.Title}`'
        text += '\n`{Author.Name}{:if,Seria.HasSeria} \\- {Seria.Name} #{Seria.Number}{:ifend} \\- {Book.Title}`'

        builder = InlineKeyboardBuilder()
        builder.button( text=f"{yesOrNo(site_config.filename,None)} По умолчанию", callback_data=f'setup_sites:save_filename:{site}:default')
        builder.button( text=f"Отмена", callback_data=f'setup_sites:save_filename:{site}:cancel')
        builder.adjust( 1, repeat=True )

        msg = await BOT.edit_message_text( chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id, text=text, reply_markup=builder.as_markup(), parse_mode="MarkdownV2" )
        await state.update_data( last_message=msg.message_id )


    @staticmethod
    async def SaveFilename( message: types.Message, state: FSMContext ) -> None:

        _filename = cleanFilename( message.text.strip() )

        sf_data = await state.get_data()

        site = sf_data['site']

        await state.clear()

        try:
            await BOT.delete_message( chat_id=message.chat.id, message_id=message.message_id )
        except:
            pass
        
        site_config = await SitesSetupController.getConfig( user_id=message.from_user.id, site=site )

        if not site_config:
            return await BOT.send_message( chat_id=message.chat.id, text="Ошибка соединения с БД. Попробуйте позднее" )

        site_config.filename = _filename

        try:
            site_config = await asyncio.wait_for( DB.SaveSiteConfig( site_config ), 5 )
        except TimeoutError as e:
            return await BOT.send_message( chat_id=message.chat.id, text="Ошибка соединения с БД. Попробуйте позднее" )

        await SitesSetupController.renderMenu( message.chat.id, sf_data['base_message'], site )


    @staticmethod
    async def SaveFilenameCallback( callback_query: types.CallbackQuery, state: FSMContext ) -> None:
        await callback_query.answer()

        await state.clear()

        data = callback_query.data.split('setup_sites:save_filename:')[1]
        site, _filename = data.split(':')
        
        site_config = await SitesSetupController.getConfig( user_id=callback_query.from_user.id, site=site )

        if not site_config:
            return await BOT.send_message( chat_id=callback_query.message.chat.id, text="Ошибка соединения с БД. Попробуйте позднее" )

        if _filename == 'default':
            site_config.filename = None

        try:
            site_config = await asyncio.wait_for( DB.SaveSiteConfig( site_config ), 5 )
        except TimeoutError as e:
            return await BOT.send_message( chat_id=callback_query.message.chat.id, text="Ошибка соединения с БД. Попробуйте позднее" )

        await SitesSetupController.renderMenu( callback_query.message.chat.id, callback_query.message.message_id, site )


    ###


    ###
    ### PROXY
    ###


    # Init proxy setup
    @staticmethod
    async def SetupProxy( callback_query: types.CallbackQuery, state: FSMContext ) -> None:
        await callback_query.answer()

        site = callback_query.data.split('setup_sites:setup_proxy:')[1]

        await state.set_state( variables.SetupSiteForm.proxy )
        await state.update_data( site=site )
        await state.update_data( base_message=callback_query.message.message_id )

        site_config = await SitesSetupController.getConfig( callback_query.from_user.id, site )

        builder = InlineKeyboardBuilder()
        builder.button( text=f"{yesOrNo(site_config.proxy,None)} По умолчанию", callback_data=f'setup_sites:save_proxy:{site}:default')
        builder.button( text=f"Отмена", callback_data=f'setup_sites:save_proxy:{site}:cancel')
        builder.adjust( 1, repeat=True )

        await state.update_data( base_message=callback_query.message.message_id )
        msg = await BOT.edit_message_text( chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id, text='Отправьте сообщением прокси\\.\nФормат:\n_http://host:port/_\n_https://host:port/_\n_socks4://host:port/_\n_socks5://host:port/_', parse_mode='MarkdownV2', reply_markup=builder.as_markup() )
        await state.update_data( last_message=msg.message_id )


    # Save proxy
    @staticmethod
    async def SaveProxy( message: types.Message, state: FSMContext ) -> None:

        sf_data = await state.get_data()

        site = sf_data['site']

        try:
            await BOT.delete_message( chat_id=message.chat.id, message_id=message.message_id )
        except:
            pass
        
        site_config = await SitesSetupController.getConfig( user_id=message.from_user.id, site=site )

        if not site_config:
            return await BOT.send_message( chat_id=message.chat.id, text="Ошибка соединения с БД. Попробуйте позднее" )

        valid_proxy = GC.proxy.match( message.text.strip() )

        if valid_proxy == None:
            await BOT.send_message( chat_id=message.chat.id, text='Невалидная прокси', reply_markup=None )
            return
        
        site_config.proxy = valid_proxy.string

        try:
            site_config = await asyncio.wait_for( DB.SaveSiteConfig( site_config ), 5 )
        except TimeoutError as e:
            return await BOT.send_message( chat_id=message.chat.id, text="Ошибка соединения с БД. Попробуйте позднее" )

        await state.clear()

        await SitesSetupController.renderMenu( message.chat.id, sf_data['base_message'], site )


    # Clear saved proxy
    @staticmethod
    async def SaveProxyCallback( callback_query: types.CallbackQuery, state: FSMContext ) -> None:
        await callback_query.answer()

        await state.clear()

        data = callback_query.data.split('setup_sites:save_proxy:')[1]
        site, _proxy = data.split(':')
        
        site_config = await SitesSetupController.getConfig( user_id=callback_query.from_user.id, site=site )

        if not site_config:
            return await BOT.send_message( chat_id=callback_query.message.chat.id, text="Ошибка соединения с БД. Попробуйте позднее" )

        if _proxy == 'default':
            site_config.proxy = None

        try:
            site_config = await asyncio.wait_for( DB.SaveSiteConfig( site_config ), 5 )
        except TimeoutError as e:
            return await BOT.send_message( chat_id=callback_query.message.chat.id, text="Ошибка соединения с БД. Попробуйте позднее" )

        await SitesSetupController.renderMenu( callback_query.message.chat.id, callback_query.message.message_id, site )


    ###


    @staticmethod
    async def getConfig( user_id: int,  site: str ) -> models.SiteConfig | None:
        try:
            site_config = await asyncio.wait_for( DB.GetSiteConfig( user_id, site ), 5 )
        except TimeoutError as e:
            return None
        
        if not site_config:
            site_config = models.SiteConfig(
                user_id=user_id,
                site=site
            )
            try:
                site_config = await asyncio.wait_for( DB.SaveSiteConfig( site_config ), 5 )
            except TimeoutError as e:
                return None
        return site_config


    @staticmethod
    async def renderMenu( chat_id: int, message_id: int,  site: str ) -> None:

        text = f"Сайт {site}\nЧто настроим?"

        site_data = await Interconnect.GetSiteData( site )

        builder = InlineKeyboardBuilder()
        if 'auth' in site_data.parameters:
            builder.button( text="Авторизация", callback_data=f"setup_sites:select_auth:{site}" )
        builder.button( text="Формат", callback_data=f"setup_sites:select_format:{site}" )
        builder.button( text="Обложка", callback_data=f"setup_sites:select_cover:{site}" )
        if 'images' in site_data.parameters:
            builder.button( text="Изображения", callback_data=f"setup_sites:select_images:{site}" )
        builder.button( text="Хэштэги", callback_data=f"setup_sites:select_hashtags:{site}" )
        builder.button( text="Название файла", callback_data=f"setup_sites:setup_filename:{site}" )
        builder.button( text="Прокси", callback_data=f"setup_sites:setup_proxy:{site}" )
        builder.button( text="Сбросить", callback_data=f"setup_sites:reset:{site}" )
        builder.button( text="Отмена", callback_data=f"setup_sites:cancel" )
        builder.adjust( 1, repeat=True )

        await BOT.edit_message_text( chat_id=chat_id, message_id=message_id, text=text, reply_markup=builder.as_markup() )