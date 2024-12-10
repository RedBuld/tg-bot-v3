import os
import ujson
import asyncio
from aiogram import Router, F, types
from aiogram.filters import Command
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
from app import schemas
from app import tools
from app import variables
from app.configs import GC
from app.objects import BOT, DP
from app.classes.interconnect import Interconnect

config_path = []

cwd = os.getcwd()

config_path.append(cwd)

if not cwd.endswith('app/') and not cwd.endswith('app'):
    config_path.append('app')

web_dir = os.path.join( *config_path, "web" )
templates = Jinja2Templates(directory=web_dir)
templates.env.filters["human_size"] = tools.human_size
templates.env.filters["punydecode"] = tools.punydecode
templates.env.filters["hideui"] = tools.hideui
templates.env.filters["pretty_json"] = tools.pretty_json

async def dumper( callback_query: types.CallbackQuery ):
    await callback_query.answer()
    print(callback_query.data)

async def register_bot_handlers() -> None:

    await AdminController.set_menu()

    router = Router()

    router.message.register( AccountSetupController.start_command, Command( commands='start' ) )
    router.message.register( AccountSetupController.setup_command, Command( commands='setup_global' ) )
    router.message.register( SitesSetupController.setup_command, Command( commands='setup_sites' ) )
    router.message.register( MiscController.uid_command, Command( commands='uid' ) )
    router.message.register( MiscController.sites_command, Command( commands='sites' ) )
    router.message.register( MiscController.stats_command, Command( commands='stats' ) )
    router.message.register( AuthController.auth_init, Command( commands='auth' ) )
    router.message.register( ExistentAuthController.existent_auths, Command( commands='auths' ) )
    router.message.register( AdminController.admin_cancel_command, Command( commands='admin_cancel' ) )
    router.message.register( AdminController.admin_cancel_batch_command, Command( commands='admin_cancel_batch' ) )
    router.message.register( AdminController.admin_reload_dc_command, Command( commands='admin_reload_dc' ) )
    router.message.register( AdminController.admin_reload_bot_command, Command( commands='admin_reload_bot' ) )
    router.message.register( AdminController.admin_leave_command, Command( commands='admin_leave' ) )
    router.message.register( AdminController.admin_queue, Command( commands='admin_queue' ) )
    router.message.register( InlineAuthController.inline_auth_login, variables.AuthForm.login )
    router.message.register( InlineAuthController.inline_auth_password, variables.AuthForm.password )
    router.message.register( AccountSetupController.setup_filename_save, variables.SetupAccountForm.filename )
    router.message.register( InlineDownloadsController.inline_download_setup_paging_start_page, variables.InlineDownloadForm.start_page )
    router.message.register( InlineDownloadsController.inline_download_setup_paging_end_page, variables.InlineDownloadForm.end_page )
    router.message.register( InlineDownloadsController.inline_download_setup_proxy_apply, variables.InlineDownloadForm.proxy )
    router.message.register( SitesSetupController.setup_filename_save, variables.SetupSiteForm.filename )
    router.message.register( DownloadsController.maybe_init_download, lambda message: message.content_type == 'text' and not message.text.startswith( '/' ) )

    router.callback_query.register( AccountSetupController.setup_start, F.data=='setup_global:start' )
    router.callback_query.register( AccountSetupController.setup_cancel, F.data=='setup_global:cancel' )
    router.callback_query.register( AccountSetupController.setup_mode, F.data=='setup_global:mode' )
    router.callback_query.register( AccountSetupController.setup_format, F.data=='setup_global:format' )
    router.callback_query.register( AccountSetupController.setup_cover, F.data=='setup_global:cover' )
    router.callback_query.register( AccountSetupController.setup_images, F.data=='setup_global:images' )
    router.callback_query.register( AccountSetupController.setup_hashtags, F.data=='setup_global:hashtags' )
    router.callback_query.register( AccountSetupController.setup_filename, F.data=='setup_global:filename' )
    router.callback_query.register( AccountSetupController.setup_mode_save, F.data.startswith('setup_global:mode:') )
    router.callback_query.register( AccountSetupController.setup_format_save, F.data.startswith('setup_global:format:') )
    router.callback_query.register( AccountSetupController.setup_cover_save, F.data.startswith('setup_global:cover:') )
    router.callback_query.register( AccountSetupController.setup_images_save, F.data.startswith('setup_global:images:') )
    router.callback_query.register( AccountSetupController.setup_hashtags_save, F.data.startswith('setup_global:hashtags:') )
    router.callback_query.register( AccountSetupController.setup_filename_save_cb, F.data.startswith('setup_global:filename:') )
    router.callback_query.register( SitesSetupController.setup_start, F.data.startswith('setup_sites:select_site:') )
    router.callback_query.register( SitesSetupController.setup_cancel, F.data=='setup_sites:cancel' )
    router.callback_query.register( SitesSetupController.setup_ignore, F.data=='setup_sites:ignore' )
    router.callback_query.register( SitesSetupController.setup_reset, F.data.startswith('setup_sites:reset:') )
    router.callback_query.register( SitesSetupController.setup_auth, F.data.startswith('setup_sites:select_auth:') )
    router.callback_query.register( SitesSetupController.setup_format, F.data.startswith('setup_sites:select_format:') )
    router.callback_query.register( SitesSetupController.setup_cover, F.data.startswith('setup_sites:select_cover:') )
    router.callback_query.register( SitesSetupController.setup_images, F.data.startswith('setup_sites:select_images:') )
    router.callback_query.register( SitesSetupController.setup_hashtags, F.data.startswith('setup_sites:select_hashtags:') )
    router.callback_query.register( SitesSetupController.setup_filename, F.data.startswith('setup_sites:select_filename:') )
    router.callback_query.register( SitesSetupController.setup_auth_save, F.data.startswith('setup_sites:save_auth:') )
    router.callback_query.register( SitesSetupController.setup_format_save, F.data.startswith('setup_sites:save_format:') )
    router.callback_query.register( SitesSetupController.setup_cover_save, F.data.startswith('setup_sites:save_cover:') )
    router.callback_query.register( SitesSetupController.setup_images_save, F.data.startswith('setup_sites:save_images:') )
    router.callback_query.register( SitesSetupController.setup_hashtags_save, F.data.startswith('setup_sites:save_hashtags:') )
    router.callback_query.register( SitesSetupController.setup_filename_save_cb, F.data.startswith('setup_sites:save_filename:') )
    router.callback_query.register( MiscController.daily_limit, F.data == 'mc:daily' )
    router.callback_query.register( DownloadsController.download_cancel, F.data.startswith('cancel_task:') )
    router.callback_query.register( WindowDownloadsController.window_download_cancel, F.data=='wdc:cancel' )
    router.callback_query.register( InlineDownloadsController.inline_download_start, F.data=='idc:download' )
    router.callback_query.register( InlineDownloadsController.inline_download_start_last, F.data=='idc:download_last' )
    router.callback_query.register( InlineDownloadsController.inline_download_cancel, F.data=='idc:cancel' )
    router.callback_query.register( InlineDownloadsController.inline_download_setup_cover, F.data=='idc:cover' )
    router.callback_query.register( InlineDownloadsController.inline_download_setup_images, F.data=='idc:images' )
    router.callback_query.register( InlineDownloadsController.inline_download_setup_format, F.data=='idc:format' )
    router.callback_query.register( InlineDownloadsController.inline_download_setup_format_apply, F.data.startswith('idc:format:') )
    router.callback_query.register( InlineDownloadsController.inline_download_setup_auth, F.data=='idc:auth' )
    router.callback_query.register( InlineDownloadsController.inline_download_setup_auth_apply, F.data.startswith('idc:auth:') )
    router.callback_query.register( InlineDownloadsController.inline_download_setup_paging, F.data=='idc:paging' )
    router.callback_query.register( InlineDownloadsController.inline_download_setup_proxy, F.data=='idc:proxy' )
    router.callback_query.register( InlineDownloadsController.inline_download_setup_proxy_empty, F.data=='idc:proxy:empty' )
    router.callback_query.register( InlineDownloadsController.inline_download_setup_proxy_cancel, F.data=='idc:proxy:cancel' )
    router.callback_query.register( InlineDownloadsController.inline_download_setup_hashtags, F.data=='idc:hashtags' )
    router.callback_query.register( InlineDownloadsController.inline_download_setup_hashtags_apply, F.data.startswith('idc:hashtags:') )
    router.callback_query.register( AuthController.auth_cancel, F.data=='auth:cancel' )
    router.callback_query.register( AuthController.auth_setup_site, F.data.startswith('auth:') )
    router.callback_query.register( WindowAuthController.window_auth_cancel, F.data=='wac:cancel' )
    router.callback_query.register( ExistentAuthController.existent_auth_cancel, F.data == 'eac:cancel' )
    router.callback_query.register( ExistentAuthController.existent_auths_map, F.data.startswith('eac:') )
    router.callback_query.register( AdminController.admin_queue_pass, F.data == 'aq:pass' )
    router.callback_query.register( AdminController.admin_queue_close, F.data == 'aq:close' )
    router.callback_query.register( AdminController.admin_queue_refresh, F.data == 'aq:refresh' )
    router.callback_query.register( AdminController.admin_queue_cancel, F.data.startswith('aq:cancel:') )

    router.callback_query.register( dumper )

    DP.include_router( router )

async def register_web_part(app: FastAPI) -> None:
    print('register_web_part')

    app.mount(f"/web", StaticFiles(directory=web_dir), name="static")

    ####

    @app.get('/auth/setup', response_class=HTMLResponse)
    async def download_setup_start( request: Request, payload: str ):
        f = Fernet(GC.encrypt_key)
        try:
            decoded = f.decrypt( payload.encode('utf-8') )
            temp = ujson.loads( decoded )
            decoded = temp
        except Exception:
            decoded = False
        decoded['host'] = GC.bot_host
        return templates.TemplateResponse("auth/index.html", {"request":request, "payload": decoded})

    @app.post('/auth/setup')
    async def handle_auth( payload: schemas.AuthSetupRequest ):
        return JSONResponse(
            status_code = 200 if await WindowAuthController.save(payload=payload) else 500,
            content = None
        )

    ####

    @app.get('/download/setup', response_class=HTMLResponse)
    async def download_setup_start( request: Request, payload: str ):
        f = Fernet(GC.encrypt_key)
        try:
            decoded = f.decrypt( payload.encode('utf-8') )
            temp = ujson.loads( decoded )
            decoded = temp
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
        decoded['host'] = GC.bot_host
        return templates.TemplateResponse("download/index.html", {"request":request, "payload": decoded, "named_formats":named_formats})

    @app.post('/download/setup')
    async def handle_download( payload: schemas.DownloadSetupRequest ):
        # print(payload)
        return JSONResponse(
            status_code = 200 if await WindowDownloadsController.save(payload=payload) else 500,
            content = None
        )
    
    ####

    @app.post('/')
    async def bot_handle( update: dict ) -> None:
        # print('#'*10)
        # print(update)
        asyncio.create_task( DP.feed_raw_update( bot=BOT, update=update ) )
        await asyncio.sleep( 0 )
        return ''

async def register_api_handlers(app: FastAPI) -> None:

    app.mount(f"/web", StaticFiles(directory=web_dir), name="static")

    @app.get('/usage', response_class=HTMLResponse)
    async def render_usage( request: Request ):
        stats = await Interconnect.GetUsage()
        # print(stats)
        return templates.TemplateResponse("usage/index.html", {"request":request, "stats":stats, "groups":GC.groups})

    @app.get('/stats', response_class=HTMLResponse)
    async def render_stats( request: Request ):
        stats = await Interconnect.GetStats()
        return templates.TemplateResponse("stats/index.html", {"request":request, "stats":stats, "groups":GC.groups})

    @app.post('/download/status')
    async def download_status( status: schemas.DownloadStatus ) -> bool:
        return JSONResponse(
            status_code = 200 if await DownloadsController.download_status(status=status) else 500,
            content = None
        )

    @app.post('/download/done')
    async def download_done( result: schemas.DownloadResult ) -> bool:
        return JSONResponse(
            status_code = 200 if await DownloadsController.download_done(result=result) else 500,
            content = None
        )

async def register_poller_part() -> None:
    print('register_poller_part')
    await DP.start_polling(BOT, polling_timeout=5, handle_signals=False)