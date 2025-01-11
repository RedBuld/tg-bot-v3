import os
import ujson
import asyncio
import logging
from aiogram import Router, F, types
from aiogram.filters import Command, StateFilter
from cryptography.fernet import Fernet
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, HTMLResponse
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

from .admin import AdminController
from .setup.account import AccountSetupController
from .setup.sites import SitesSetupController
from .downloads import DownloadsController
from .downloads.window import WindowDownloadsController
from .downloads.inline import InlineDownloadsController
from .auth import AuthController
from .auth.window import WindowAuthController
from .auth.inline import InlineAuthController
from .auth.existent import ExistentAuthController
from .misc import MiscController

from app import tools
from app import dto
from app import tools
from app import variables
from app.configs import GC
from app.objects import BOT, DP
from app.classes.interconnect import Interconnect

logger = logging.getLogger(__name__)

web_dir = '/app/web'
templates = Jinja2Templates(directory=web_dir)
templates.env.filters["human_size"] = tools.humanizeSize
templates.env.filters["punydecode"] = tools.punyDecode
templates.env.filters["hideui"] = tools.hideUI
templates.env.filters["pretty_json"] = tools.prettyJSON

async def register_bot_handlers() -> None:

    await AdminController.SetBotMenu()

    router = Router()


    # Global settings
    router.message.register(        AccountSetupController.Start, Command( 'start' ) )
    router.message.register(        AccountSetupController.SelectOption, Command( 'setup' ) )
    router.message.register(        AccountSetupController.SelectOption, Command( 'setup_global' ) )
    router.callback_query.register( AccountSetupController.StartSetup, F.data=='setup_global:start' )
    router.callback_query.register( AccountSetupController.CancelSetup, F.data=='setup_global:cancel' )
    router.callback_query.register( AccountSetupController.SelectMode, F.data=='setup_global:mode' )
    router.callback_query.register( AccountSetupController.SaveMode, F.data.startswith('setup_global:mode:') )
    router.callback_query.register( AccountSetupController.SelectFormat, F.data=='setup_global:format' )
    router.callback_query.register( AccountSetupController.SaveFormat, F.data.startswith('setup_global:format:') )
    router.callback_query.register( AccountSetupController.SelectCover, F.data=='setup_global:cover' )
    router.callback_query.register( AccountSetupController.SaveCover, F.data.startswith('setup_global:cover:') )
    router.callback_query.register( AccountSetupController.SelectImages, F.data=='setup_global:images' )
    router.callback_query.register( AccountSetupController.SaveImages, F.data.startswith('setup_global:images:') )
    router.callback_query.register( AccountSetupController.SelectHashtags, F.data=='setup_global:hashtags' )
    router.callback_query.register( AccountSetupController.SaveHashtags, F.data.startswith('setup_global:hashtags:') )
    router.callback_query.register( AccountSetupController.SetupFilename, F.data=='setup_global:filename' )
    router.message.register(        AccountSetupController.SaveFilename, StateFilter( variables.SetupAccountForm.filename ) )
    router.callback_query.register( AccountSetupController.SaveFilenameCallback, F.data.startswith('setup_global:filename:') )


    # Site-based settings
    router.message.register(        SitesSetupController.SelectSite, Command( 'setup_sites' ) )
    router.callback_query.register( SitesSetupController.StartSetup, F.data.startswith('setup_sites:select_site:') )
    router.callback_query.register( SitesSetupController.CancelSetup, F.data=='setup_sites:cancel' )
    router.callback_query.register( SitesSetupController.ResetSiteConfig, F.data.startswith('setup_sites:reset:') )
    router.callback_query.register( SitesSetupController.SelectAuth, F.data.startswith('setup_sites:select_auth:') )
    router.callback_query.register( SitesSetupController.SaveAuth, F.data.startswith('setup_sites:save_auth:') )
    router.callback_query.register( SitesSetupController.SelectFormat, F.data.startswith('setup_sites:select_format:') )
    router.callback_query.register( SitesSetupController.SaveFormat, F.data.startswith('setup_sites:save_format:') )
    router.callback_query.register( SitesSetupController.SelectCover, F.data.startswith('setup_sites:select_cover:') )
    router.callback_query.register( SitesSetupController.SaveCover, F.data.startswith('setup_sites:save_cover:') )
    router.callback_query.register( SitesSetupController.SelectThumbnail, F.data.startswith('setup_sites:select_thumb:') )
    router.callback_query.register( SitesSetupController.SaveThumbnail, F.data.startswith('setup_sites:save_thumb:') )
    router.callback_query.register( SitesSetupController.SelectImages, F.data.startswith('setup_sites:select_images:') )
    router.callback_query.register( SitesSetupController.SaveImages, F.data.startswith('setup_sites:save_images:') )
    router.callback_query.register( SitesSetupController.SelectHashtags, F.data.startswith('setup_sites:select_hashtags:') )
    router.callback_query.register( SitesSetupController.SaveHashtags, F.data.startswith('setup_sites:save_hashtags:') )
    router.callback_query.register( SitesSetupController.SetupFilename, F.data.startswith('setup_sites:setup_filename:') )
    router.message.register(        SitesSetupController.SaveFilename, StateFilter( variables.SetupSiteForm.filename ) )
    router.callback_query.register( SitesSetupController.SaveFilenameCallback, F.data.startswith('setup_sites:save_filename:') )
    router.callback_query.register( SitesSetupController.SetupProxy, F.data.startswith('setup_sites:setup_proxy:') )
    router.message.register(        SitesSetupController.SaveProxy, StateFilter( variables.SetupSiteForm.proxy ) )
    router.callback_query.register( SitesSetupController.SaveProxyCallback, F.data.startswith('setup_sites:save_proxy:') )


    # Misc
    router.message.register(        MiscController.ShowAllowedSites, Command( 'sites' ) )
    router.message.register(        MiscController.GetMyUID, Command( 'uid' ) )
    router.message.register(        MiscController.StatsMenu, Command( 'stats' ) )
    router.callback_query.register( MiscController.DailyLimit, F.data == 'mc:daily' )
    router.message.register(        MiscController.Panic, Command( 'panic' ) )
    router.callback_query.register( MiscController.PanicReset, F.data == 'panic:reset' )


    # Auths
    router.message.register(        AuthController.StartAuth, Command( 'auth' ) )
    router.callback_query.register( AuthController.CancelAuth, F.data=='auth:cancel' )
    router.callback_query.register( AuthController.SelectSite, F.data.startswith('auth:') )
    #
    router.message.register(        InlineAuthController.HandleLogin, StateFilter( variables.AuthForm.login ), F.content_type.in_( { 'text' } ), ~F.text.startswith( '/' ) )
    router.message.register(        InlineAuthController.HandlePassword, StateFilter( variables.AuthForm.password ), F.content_type.in_( { 'text' } ), ~F.text.startswith( '/' ) )
    #
    router.message.register(        ExistentAuthController.ListAuthedSites, Command( 'auths' ) )
    router.callback_query.register( ExistentAuthController.AuthActions, F.data.startswith('eac:') )
    router.callback_query.register( ExistentAuthController.Cancel, F.data == 'eac:cancel' )


    # Admin
    router.message.register(        AdminController.CancelTask, Command( 'admin_cancel' ) )
    router.message.register(        AdminController.CancelTasks, Command( 'admin_cancel_batch' ) )
    router.message.register(        AdminController.ReloadDownloadCenter, Command( 'admin_reload_dc' ) )
    router.message.register(        AdminController.ReloadBot, Command( 'admin_reload_bot' ) )
    router.message.register(        AdminController.StopTasks, Command( 'admin_stop_tasks' ) )
    router.message.register(        AdminController.StartTasks, Command( 'admin_start_tasks' ) )
    router.message.register(        AdminController.StopResults, Command( 'admin_stop_results' ) )
    router.message.register(        AdminController.StartResults, Command( 'admin_start_results' ) )
    router.message.register(        AdminController.StopQueue, Command( 'admin_stop_queue' ) )
    router.message.register(        AdminController.StartQueue, Command( 'admin_start_queue' ) )
    router.message.register(        AdminController.LeaveChat, Command( 'admin_leave' ) )
    # router.message.register( AdminController.Queue, Command( 'admin_queue' ) )
    # router.callback_query.register( AdminController.admin_queue_pass, F.data == 'aq:pass' )
    # router.callback_query.register( AdminController.admin_queue_close, F.data == 'aq:close' )
    # router.callback_query.register( AdminController.admin_queue_refresh, F.data == 'aq:refresh' )
    # router.callback_query.register( AdminController.admin_queue_cancel, F.data.startswith('aq:cancel:') )


    # Downloads
    router.callback_query.register( DownloadsController.CancelTask, F.data.startswith('cancel_task:') )
    #
    router.callback_query.register( WindowDownloadsController.CancelSetup, F.data=='wdc:cancel' )
    #
    router.message.register(        DownloadsController.MaybeInitDownload, StateFilter( None ), F.content_type.in_( { 'text' } ), ~F.text.startswith( '/' ) )
    router.callback_query.register( InlineDownloadsController.SetAdvancedSetupMode, F.data=='idc:advanced_mode' )
    router.callback_query.register( InlineDownloadsController.SetBaseSetupMode, F.data=='idc:base_mode' )
    router.callback_query.register( InlineDownloadsController.StartDownload, F.data=='idc:download' )
    router.callback_query.register( InlineDownloadsController.DownloadOnlyLastChapter, F.data=='idc:download_last' )
    router.callback_query.register( InlineDownloadsController.CancelDownloadSetup, F.data=='idc:cancel' )
    router.callback_query.register( InlineDownloadsController.ToggleCover, F.data=='idc:cover' )
    router.callback_query.register( InlineDownloadsController.ToggleThumbnail, F.data=='idc:thumb' )
    router.callback_query.register( InlineDownloadsController.ToggleImages, F.data=='idc:images' )
    router.callback_query.register( InlineDownloadsController.SelectAuth, F.data=='idc:auth' )
    router.callback_query.register( InlineDownloadsController.SaveAuth, F.data.startswith('idc:auth:') )
    router.callback_query.register( InlineDownloadsController.SelectFormat, F.data=='idc:format' )
    router.callback_query.register( InlineDownloadsController.SaveFormat, F.data.startswith('idc:format:') )
    router.callback_query.register( InlineDownloadsController.SetupPages, F.data=='idc:paging' )
    router.message.register(        InlineDownloadsController.HandleStartPage, StateFilter( variables.InlineDownloadForm.start_page ) )
    router.message.register(        InlineDownloadsController.HandleEndPage, StateFilter( variables.InlineDownloadForm.end_page ) )
    router.callback_query.register( InlineDownloadsController.SetupProxy, F.data=='idc:proxy' )
    router.message.register(        InlineDownloadsController.SaveProxy, StateFilter( variables.InlineDownloadForm.proxy ) )
    router.callback_query.register( InlineDownloadsController.EmptyProxy, F.data=='idc:proxy:empty' )
    router.callback_query.register( InlineDownloadsController.CancelProxySetup, F.data=='idc:proxy:cancel' )
    router.callback_query.register( InlineDownloadsController.SelectHashtags, F.data=='idc:hashtags' )
    router.callback_query.register( InlineDownloadsController.SaveHashtags, F.data.startswith('idc:hashtags:') )

    DP.include_router( router )


async def register_web_part( app: FastAPI ) -> None:
    logger.info('Running in web mode')

    app.mount(f"/web", StaticFiles(directory=web_dir), name="static")

    ####

    @app.get('/auth/setup', response_class=HTMLResponse)
    async def download_setup_start( request: Request, payload: str ):
        f = Fernet( GC.encrypt_key )
        try:
            decoded = f.decrypt( payload.encode('utf-8') )
            temp = ujson.loads( decoded )
            decoded = temp
            decoded['host'] = GC.url
        except Exception:
            decoded = False
        return templates.TemplateResponse("auth/index.html", {"request":request, "payload": decoded})

    @app.post('/auth/setup')
    async def handle_auth( payload: dto.AuthSetupRequest ):
        return JSONResponse(
            status_code = 200 if await WindowAuthController.Save(payload=payload) else 500,
            content = None
        )

    ####

    @app.get('/download/setup', response_class=HTMLResponse)
    async def download_setup_start( request: Request, payload: str ):
        f = Fernet( GC.encrypt_key )
        try:
            decoded = f.decrypt( payload.encode('utf-8') )
            temp = ujson.loads( decoded )
            decoded = temp
            decoded['host'] = GC.url
        except Exception:
            decoded = False
        if decoded:
            named_formats = {}
            if 'formats' in decoded:
                for x in decoded['formats']:
                    if x in GC.formats:
                        named_formats[x] = GC.formats[x]
        else:
            named_formats = {}
        return templates.TemplateResponse("download/index.html", {"request":request, "payload": decoded, "named_formats":named_formats})

    @app.post('/download/setup')
    async def handle_download( payload: dto.DownloadSetupRequest ):
        return JSONResponse(
            status_code = 200 if await WindowDownloadsController.Save( payload=payload ) else 500,
            content = None
        )
    
    ####

    @app.post('/')
    async def bot_handle( update: dict ) -> None:
        asyncio.create_task( DP.feed_raw_update( bot=BOT, update=update ) )
        await asyncio.sleep( 0 )
        return ''


async def register_api_handlers( app: FastAPI ) -> None:

    app.mount(f"/web", StaticFiles(directory=web_dir), name="static")

    @app.get('/usage', response_class=HTMLResponse)
    async def render_usage( request: Request ):
        stats = await Interconnect.GetUsage()
        return templates.TemplateResponse(
            "usage/index.html",
            {
                "request": request,
                "stats":   stats,
                "groups":  GC.groups
            }
        )

    @app.get('/stats', response_class=HTMLResponse)
    async def render_stats( request: Request ):
        stats = await Interconnect.GetStats()
        return templates.TemplateResponse(
            "stats/index.html",
            {
                "request": request,
                "stats":   stats,
                "groups":  GC.groups
            }
        )

    @app.post('/download/status')
    async def download_status( status: dto.DownloadStatus ) -> bool:
        return JSONResponse(
            status_code = 200 if await DownloadsController.DownloadStatus( status=status ) else 500,
            content = None
        )

    @app.post('/download/done')
    async def download_done( result: dto.DownloadResult ) -> bool:
        return JSONResponse(
            status_code = 200 if await DownloadsController.DownloadDone( result=result ) else 500,
            content = None
        )


async def register_poller_part() -> None:
    logger.info('Running in polling mode')
    await DP.start_polling( BOT, polling_timeout=5, handle_signals=False )