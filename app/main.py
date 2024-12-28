import os
import asyncio
setattr(asyncio.sslproto._SSLProtocolTransport, "_start_tls_compatible", True)
import logging
from dotenv import load_dotenv
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError, ResponseValidationError

try:
    load_dotenv(".env")
except:
    pass

if not os.environ.get("BOT_TOKEN"):
    raise Exception('provide BOT_TOKEN in env')

from app.configs import GC
from app.objects import DB, BOT
from app.handlers import register_bot_handlers, register_api_handlers, register_web_part, register_poller_part


####

logging.basicConfig(
    # filename='/srv/tg-bot-v3/log.log',
    format='\x1b[32m%(levelname)s\x1b[0m:     %(name)s[%(process)d] %(asctime)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def request_validation_error_exception_handler( request: Request, exc: RequestValidationError ):
    validation_errors = exc.errors()
    return JSONResponse(
        status_code = 500,
        content =     { "detail": [ str( err ) for err in validation_errors ] }
    )

async def response_validation_error_exception_handler( request: Request, exc: ResponseValidationError ):
    validation_errors = exc.errors()
    return JSONResponse(
        status_code = 500,
        content =     { "detail": [ str( err ) for err in validation_errors ] }
    )

async def base_error_exception_handler( request: Request, exc: Exception ):
    return JSONResponse(
        status_code = 500,
        content =     { "detail": str( exc ) }
    )

####

async def read_config():
    await GC.UpdateConfig()
    await DB.UpdateConfig()

async def db_start() -> None:
    await DB.Start()

async def db_stop() -> None:
    await DB.Stop()

async def bot_start() -> None:
    if BOT and GC.url:
        await BOT.set_webhook( GC.url, drop_pending_updates=False )

async def bot_stop() -> None:
    if BOT and GC.url:
        await BOT.delete_webhook()
        await BOT.session.close()

####

@asynccontextmanager
async def lifespan( app: FastAPI ):
    await read_config()
    await db_start()
    await bot_start()
    await init(app)
    yield
    await bot_stop()
    await db_stop()

app = FastAPI( 
    docs_url=None,
    openapi_url=None,
    exception_handlers={
        RequestValidationError: request_validation_error_exception_handler,
        ResponseValidationError: response_validation_error_exception_handler,
        Exception: base_error_exception_handler
    },
    lifespan=lifespan
)

async def init(app: FastAPI) -> None:
    await register_bot_handlers()
    await register_api_handlers(app)

    if GC.url:
        asyncio.create_task( register_web_part(app) )
    else:
        asyncio.create_task( register_poller_part() )