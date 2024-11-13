from python_event_bus import EventBus
from aiogram import Dispatcher, Router, F, types
from aiogram.filters import Command

from .setup import AccountSetupController
from .downloads import DownloadsController
from .downloads.inline import InlineDownloadsController
from .downloads.window import WindowDownloadsController
from .auth import AuthController
from .auth.window import WindowAuthController
from .auth.inline import InlineAuthController
from .auth.existent import ExistentAuthController
from .misc import MiscController
from app.configs import GC
from app.objects import DB, RD, BOT, DP
from app import variables

ASC = AccountSetupController()
DC = DownloadsController()
IDC = InlineDownloadsController()
WDC = WindowDownloadsController()
AC = AuthController()
IAC = InlineAuthController()
WAC = WindowAuthController()
EAC = ExistentAuthController()
MC = MiscController()

def register_bot_handlers():
    router = Router()

    # MESSAGES_HANDLERS
    router.message.register( ASC.start_command, Command( commands='start' ) )
    router.message.register( ASC.setup_command, Command( commands='setup' ) )
    router.message.register( MC.uid_command, Command( commands='uid' ) )
    router.message.register( MC.sites_command, Command( commands='sites' ) )
    router.message.register( AC.auth_init, Command( commands='auth' ) )
    router.message.register( EAC.existent_auths, Command( commands='auths' ) )
    
    router.message.register( IAC.inline_auth_login, variables.AuthForm.login )
    router.message.register( IAC.inline_auth_password, variables.AuthForm.password )

    router.message.register( IDC.inline_download_setup_paging_start_page, variables.InlineDownloadForm.start_page )
    router.message.register( IDC.inline_download_setup_paging_end_page, variables.InlineDownloadForm.end_page )

    router.message.register( DC.maybe_init_download, lambda message: message.content_type == 'text' and not message.text.startswith( '/' ) )


    # CALLBACKS_HANDLERS

    # SetupController
    router.callback_query.register( ASC.account_setup_start, F.data=='setup:start' )
    router.callback_query.register( ASC.account_setup_cancel, F.data=='setup:cancel' )
    router.callback_query.register( ASC.account_setup_mode, F.data=='setup:mode' )
    router.callback_query.register( ASC.account_setup_format, F.data=='setup:format' )
    router.callback_query.register( ASC.account_setup_cover, F.data=='setup:cover' )
    router.callback_query.register( ASC.account_setup_images, F.data=='setup:images' )
    router.callback_query.register( ASC.account_setup_mode_save, F.data.startswith('setup:mode:') )
    router.callback_query.register( ASC.account_setup_format_save, F.data.startswith('setup:format:') )
    router.callback_query.register( ASC.account_setup_cover_save, F.data.startswith('setup:cover:') )
    router.callback_query.register( ASC.account_setup_images_save, F.data.startswith('setup:images:') )

    # DownloadsController
    router.callback_query.register( DC.download_cancel, F.data.startswith('cancel_task:') )
    # InlineDownloadsController
    router.callback_query.register( IDC.inline_download_start, F.data=='idc:download' )
    router.callback_query.register( IDC.inline_download_start_last, F.data=='idc:download_last' )
    router.callback_query.register( IDC.inline_download_cancel, F.data=='idc:cancel' )
    router.callback_query.register( IDC.inline_download_setup_cover, F.data=='idc:cover' )
    router.callback_query.register( IDC.inline_download_setup_images, F.data=='idc:images' )
    router.callback_query.register( IDC.inline_download_setup_format, F.data=='idc:format' )
    router.callback_query.register( IDC.inline_download_setup_format_apply, F.data.startswith('idc:format:') )
    router.callback_query.register( IDC.inline_download_setup_auth, F.data=='idc:auth' )
    router.callback_query.register( IDC.inline_download_setup_auth_apply, F.data.startswith('idc:auth:') )
    router.callback_query.register( IDC.inline_download_setup_paging, F.data=='idc:paging' )
    # WindowDownloadsController
    router.callback_query.register( WDC.window_download_cancel, F.data=='wdc:cancel' )

    # AuthController
    router.callback_query.register( AC.auth_cancel, F.data=='auth:cancel' )
    router.callback_query.register( AC.auth_setup_site, F.data.startswith('auth:') )
    # ExistentAuthController
    router.callback_query.register( EAC.existent_auth_cancel, F.data == 'eac:cancel' )
    router.callback_query.register( EAC.existent_auths_map, F.data.startswith('eac:') )
    # WindowAuthController
    router.callback_query.register( WAC.window_auth_cancel, F.data=='wac:cancel' )


    DP.include_router( router )