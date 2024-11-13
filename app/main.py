# -*- coding: utf-8 -*-

import os
import re
from dotenv import load_dotenv
if os.name == 'nt':
    load_dotenv(".env.development")
else:
    load_dotenv(".env")

import time
import traceback
import ujson
import aiohttp
import asyncio
import logging
from asyncache import cached
from cachetools import TTLCache
from cryptography.fernet import Fernet
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
from python_event_bus import EventBus
from app import schemas
from app.configs import GC
from app.objects import DB, BOT, DP
from app.handlers import register_bot_handlers


####

logging.basicConfig(
    filename='/srv/tg-bot-v3/log.log',
    format='\x1b[32m%(levelname)s\x1b[0m:     %(name)s[%(process)d] %(asctime)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def request_validation_error_exception_handler( request: Request, exc: RequestValidationError ):
    print( exc )
    validation_errors = exc.errors()
    print(validation_errors)
    return JSONResponse(
        status_code = 500,
        content =     { "detail": [ str( err ) for err in validation_errors ] }
    )

async def response_validation_error_exception_handler( request: Request, exc: ResponseValidationError ):
    print( exc )
    validation_errors = exc.errors()
    return JSONResponse(
        status_code = 500,
        content =     { "detail": [ str( err ) for err in validation_errors ] }
    )

async def base_error_exception_handler( request: Request, exc: Exception ):
    print( exc )
    return JSONResponse(
        status_code = 500,
        content =     { "detail": str( exc ) }
    )

####

# @DP.update()
# async def message_handler(update) -> None:
#     print('update not handled')
#     print(update)


@asynccontextmanager
async def lifespan( app: FastAPI ):
    await read_config()
    await db_start()
    await bot_start()
    yield
    await bot_stop()
    await db_stop()

#UPDATE CONFIG
async def read_config():
    await GC.updateConfig()
    await DB.updateConfig()

# DB
async def db_start():
    await DB.Start()

async def db_stop():
    await DB.Stop()

# BOT
async def bot_start() -> None:
    wh = await BOT.set_webhook( GC.bot_host, drop_pending_updates=True )
    logger.info( 'wh -> ' + GC.bot_host + ' -> ' +  str( wh ) )

async def bot_stop() -> None:
    if BOT:
        await BOT.delete_webhook()
        await BOT.session.close()



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

register_bot_handlers()

def human_size(size: int) -> str:
    ext = "б"
    if size > 10240:
        size = size / 1024
        ext = "Кб"
    if size > 10240:
        size = size / 1024
        ext = "Мб"
    if size > 10240:
        size = size / 1024
        ext = "Гб"
    if size > 10240:
        size = size / 1024
        ext = "Тб"
    size = round(float(size),2)
    return f"{size} {ext}"

def punydecode(site: str) -> str:
    return site.encode().decode('idna')

def hideui(url: str) -> str:
    return re.sub(r"&?ui=\d+", "", url)

web_dir = os.path.join(os.path.dirname(__file__), "web")
templates = Jinja2Templates(directory=web_dir)
templates.env.filters["human_size"] = human_size
templates.env.filters["punydecode"] = punydecode
templates.env.filters["hideui"] = hideui
app.mount("/web", StaticFiles(directory=web_dir), name="static")

###


@cached(TTLCache(128, 5))
async def get_usage():
    stats = {}
    _attempts = 0
    try:
        async with aiohttp.ClientSession(json_serialize=ujson.dumps) as session:
            async with session.get( GC.queue_host + 'export/queue', verify_ssl=False ) as response:
                if response.status == 200:
                    _attempts = 5
                    stats = await response.json()
                else:
                    _attempts+=1
                    await asyncio.sleep(1)
    except:
        _attempts+=1
        await asyncio.sleep(1)
    return stats

@cached(TTLCache(128, 5))
async def get_stats():
    stats = {}
    _attempts = 0
    try:
        async with aiohttp.ClientSession(json_serialize=ujson.dumps) as session:
            async with session.get( GC.queue_host + 'export/stats', verify_ssl=False ) as response:
                if response.status == 200:
                    _attempts = 5
                    stats = await response.json()
                else:
                    _attempts+=1
                    await asyncio.sleep(1)
    except:
        _attempts+=1
        await asyncio.sleep(1)
    return stats

@app.get('/usage', response_class=HTMLResponse)
async def render_usage( request: Request ):
    stats = await get_usage()
    groups = {
        "books": "Книги",
        "manga": "Манга",
        "ranobe": "Ранобэ",
        "audiobooks": "Аудиокниги",
        "pdf": "PDF-книги",
    }
    return templates.TemplateResponse("usage/index.html", {"request":request, "stats":stats, "groups":groups})

@app.get('/stats', response_class=HTMLResponse)
async def render_stats( request: Request ):
    stats = await get_stats()
    groups = {
        "books": "Книги",
        "manga": "Манга",
        "ranobe": "Ранобэ",
        "audiobooks": "Аудиокниги",
        "pdf": "PDF-книги",
    }
    return templates.TemplateResponse("stats/index.html", {"request":request, "stats":stats, "groups":groups})

###


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
    from app.handlers import WAC
    return JSONResponse(
        status_code = 200 if await WAC._save(payload=payload) else 500,
        content = None
    )


###


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
    from app.handlers import WDC
    print(payload)
    return JSONResponse(
        status_code = 200 if await WDC._save(payload=payload) else 500,
        content = None
    )


###


@app.post('/download/status')
async def download_status( status: schemas.DownloadStatus ) -> bool:
    from app.handlers import DC
    return JSONResponse(
        status_code = 200 if await DC.download_status(status=status) else 500,
        content = None
    )

@app.post('/download/done')
async def download_done( result: schemas.DownloadResult ) -> bool:
    from app.handlers import DC
    return JSONResponse(
        status_code = 200 if await DC.download_done(result=result) else 500,
        content = None
    )


###


@app.post('/')
async def bot_handle( update: dict ) -> None:
    print('#'*10)
    print(update)
    asyncio.create_task( DP.feed_raw_update( bot=BOT, update=update ) )
    await asyncio.sleep( 0 )
    return ''