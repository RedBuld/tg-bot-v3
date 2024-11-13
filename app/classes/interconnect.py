from __future__ import annotations
import asyncio
import aiohttp
import ujson
import traceback
import logging
from aiohttp.client_exceptions import ClientError
from typing import List, Dict, Any
from asyncache import cached
from cachetools import TTLCache
from app import variables
from app import schemas
from app.configs import GC

logger = logging.getLogger(__name__)

class Interconnect():

    @cached(TTLCache(128, 60))
    async def GetSiteData( self, site_name: str ) -> tuple[ bool, List[ str ], Dict[ str, List[ str ] ] ]:
        async with aiohttp.ClientSession( json_serialize=ujson.dumps ) as session:
            async with session.post( GC.queue_host + 'sites/check', json=schemas.SiteCheckRequest(site = site_name).model_dump(mode='json'), verify_ssl=False ) as response:
                if response.status == 200:
                    data = await response.json( loads=ujson.loads )
                    res = schemas.SiteCheckResponse( **data )
                    return res.allowed, res.parameters, res.formats


    async def InitDownload( self, request: schemas.DownloadRequest ) -> int | str:
        try:
            async with aiohttp.ClientSession( json_serialize=ujson.dumps ) as session:
                async with session.post( GC.queue_host + 'download/new', json=request.model_dump(mode='json'), verify_ssl=False ) as response:
                    if response.status == 200:
                        task_id = int( await response.json( loads=ujson.loads ) )
                        return task_id
                    else:
                        message = await response.json( loads=ujson.loads )
                        return message
        except ClientError as e:
            return "Ошибка соединения с сервером загрузки"
        except Exception as e:
            return str(e)


    async def CancelDownload( self, request: schemas.DownloadCancelRequest ) -> bool | str:
        try:
            async with aiohttp.ClientSession(json_serialize=ujson.dumps) as session:
                async with session.post( GC.queue_host + 'download/cancel', json=request.model_dump(mode='json'), verify_ssl=False ) as response:
                    return True
        except ClientError as e:
            return "Ошибка соединения с сервером загрузки"
        except Exception as e:
            return str(e)


    async def ClearDownloadFiles( self, request: schemas.DownloadClearRequest ) -> None:
        _attempts = 0
        while _attempts < 5:
            try:
                async with aiohttp.ClientSession( json_serialize=ujson.dumps ) as session:
                    async with session.post( GC.queue_host + 'download/clear', json=request.model_dump(mode='json'), verify_ssl=False ) as response:
                        if response.status == 200:
                            _attempts = 5
                        else:
                            _attempts+=1
                            await asyncio.sleep(5)
            except:
                traceback.print_exc()
                _attempts+=1
                await asyncio.sleep(5)