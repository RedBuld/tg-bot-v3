from __future__ import annotations
import asyncio
import aiohttp
import ujson
import traceback
import logging
import hashlib
from aiohttp.client_exceptions import ClientError
from typing import List, Dict, Any
from app import variables
from app import schemas
from app.configs import GC
from app.objects import RD

logger = logging.getLogger(__name__)

class Interconnect:

    @staticmethod
    async def GetSitesActive() -> List[ str ] | str:
        model = schemas.SiteListResponse
        cached = await RD.get(variables.ACTIVE_SITES_CACHE_KEY)

        if not cached:
            _attempts = 0
            while _attempts < 5:
                try:
                    async with aiohttp.ClientSession( json_serialize=ujson.dumps ) as session:
                        async with session.post( GC.queue_host + 'sites/active', verify_ssl=False ) as response:
                            if response.status == 200:
                                data = await response.json( loads=ujson.loads )
                                model = model.model_validate( data )
                                _attempts = 5
                except:
                    traceback.print_exc()
                    _attempts+=1
                    await asyncio.sleep(5)

            cached = model.model_dump_json()
            await RD.setex(variables.ACTIVE_SITES_CACHE_KEY, 60, cached)
        else:
            model = model.model_validate_json( cached )

        return model.sites

    @staticmethod
    async def GetSitesWithAuth() -> List[str]:
        model = schemas.SiteListResponse
        cached = await RD.get(variables.AUTH_SITES_CACHE_KEY)

        if not cached:
            _attempts = 0
            while _attempts < 5:
                try:
                    async with aiohttp.ClientSession( json_serialize=ujson.dumps ) as session:
                        async with session.post( GC.queue_host + 'sites/auths', verify_ssl=False ) as response:
                            if response.status == 200:
                                data = await response.json( loads=ujson.loads )
                                model = model.model_validate( data )
                                _attempts = 5
                except:
                    traceback.print_exc()
                    _attempts+=1
                    await asyncio.sleep(5)

            cached = model.model_dump_json()
            await RD.setex(variables.AUTH_SITES_CACHE_KEY, 60, cached)
        else:
            model = model.model_validate_json( cached )

        return model.sites

    @staticmethod
    async def GetSiteData( site_name: str ) -> schemas.SiteCheckResponse:
        cache_key = f"cache_sites_data_{site_name}"
        model = schemas.SiteCheckResponse
        cached = await RD.get(cache_key)

        if not cached:
            _attempts = 0
            while _attempts < 5:
                try:
                    async with aiohttp.ClientSession( json_serialize=ujson.dumps ) as session:
                        async with session.post( GC.queue_host + 'sites/check', json=schemas.SiteCheckRequest(site = site_name).model_dump(mode='json'), verify_ssl=False ) as response:
                            if response.status == 200:
                                data = await response.json( loads=ujson.loads )
                                model = model.model_validate( data )
                                _attempts = 5
                except:
                    traceback.print_exc()
                    _attempts+=1
                    await asyncio.sleep(5)

            cached = model.model_dump_json()
            await RD.setex(cache_key, 60, cached)
        else:
            model = model.model_validate_json( cached )

        return model

    @staticmethod
    async def GetUsage(use_cache: bool = True) -> Dict[ str, Any ]:
        if use_cache:
            cached = await RD.get(variables.USAGE_CACHE_KEY)
        else:
            cached = None

        if not cached:
            stats = {}
            _attempts = 0
            while _attempts < 5:
                try:
                    async with aiohttp.ClientSession(json_serialize=ujson.dumps) as session:
                        async with session.get( GC.queue_host + 'export/queue', verify_ssl=False ) as response:
                            if response.status == 200:
                                _attempts = 5
                                stats = await response.json( loads=ujson.loads )
                except:
                    _attempts+=1
                    await asyncio.sleep(1)
            
            cached = ujson.dumps(stats)
            await RD.setex(variables.USAGE_CACHE_KEY, 5, cached)
        else:
            stats = ujson.loads(cached)

        return stats

    @staticmethod
    async def GetStats() -> Dict[ str, Any ]:
        cached = await RD.get(variables.STATS_CACHE_KEY)

        if not cached:
            stats = {}
            _attempts = 0
            while _attempts < 5:
                try:
                    async with aiohttp.ClientSession(json_serialize=ujson.dumps) as session:
                        async with session.get( GC.queue_host + 'export/stats', verify_ssl=False ) as response:
                            if response.status == 200:
                                _attempts = 5
                                stats = await response.json( loads=ujson.loads )
                except:
                    _attempts+=1
                    await asyncio.sleep(1)
            
            cached = ujson.dumps(stats)
            await RD.setex(variables.STATS_CACHE_KEY, 5, cached)
        else:
            stats = ujson.loads(cached)

        return stats
    

    ######################


    @staticmethod
    async def InitDownload( request: schemas.DownloadRequest ) -> int | str:
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


    @staticmethod
    async def CancelDownload( request: schemas.DownloadCancelRequest ) -> schemas.DownloadCancelResponse | str:
        try:
            async with aiohttp.ClientSession(json_serialize=ujson.dumps) as session:
                async with session.post( GC.queue_host + 'download/cancel', json=request.model_dump(mode='json'), verify_ssl=False ) as response:
                    if response.status == 200:
                        try:
                            data = await response.json( loads=ujson.loads )
                            return schemas.DownloadCancelResponse.model_validate( data )
                        except:
                            traceback.print_exc()
                            return 'Загрузка не найдена'
                    else:
                        message = await response.json( loads=ujson.loads )
                        return message
        except ClientError as e:
            return "Ошибка соединения с сервером загрузки"
        except Exception as e:
            return str(e)


    @staticmethod
    async def ClearDownloadFiles( request: schemas.DownloadClearRequest ) -> None:
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

    @staticmethod
    async def ReloadConfig() -> None:
        _attempts = 0
        while _attempts < 5:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get( GC.queue_host + 'update_config', verify_ssl=False ) as response:
                        if response.status == 200:
                            _attempts = 5
                        else:
                            _attempts+=1
                            await asyncio.sleep(5)
            except:
                traceback.print_exc()
                _attempts+=1
                await asyncio.sleep(5)

    @staticmethod
    async def CheckLink( link: str ) -> bool:
        cache_key = "check_link_" + str( hashlib.md5( link.encode('utf-8') ).hexdigest() )
        allowed = await RD.getex(cache_key)
        print('CheckLink',link,allowed)

        async def _check_site(session: aiohttp.ClientSession, link: str) -> int|str:
            async with session.get( link, verify_ssl=False ) as response:
                if response.status == 404:
                    return 0
                else:
                    text = await response.text()
                    print('_check_site_text',text)
                    url = str(response.real_url)
                    if 'mature?path=' in url:
                        return url
                    if 'заблокирована на территории РФ' in text:
                        return 0
                    else:
                        return 1

        async def _rulate_mature(session: aiohttp.ClientSession, link: str) -> int:
            path = link.split('mature?path=')[1]
            async with session.post( link, verify_ssl=False, data={"path":path,"ok":"Да"} ) as response:
                if response.status == 404:
                    return 0
                else:
                    text = await response.text()
                    if 'заблокирована на территории РФ' in text:
                        return 0
                    else:
                        return 1

        if allowed == None:
            _attempts = 0
            async with aiohttp.ClientSession() as session:
                while _attempts < 5:
                    try:
                        allowed = await _check_site(session, link)
                        print('_check_site 1',allowed)
                        if type(allowed) == str:
                            test = await _rulate_mature(session, allowed)
                            allowed = await _check_site(session, link)
                            print('_check_site 2',allowed)
                        _attempts = 5
                    except:
                        traceback.print_exc()
                        _attempts+=1
                        await asyncio.sleep(5)
            await RD.setex(cache_key, 3600, allowed)
        else:
            allowed = int(allowed)

        allowed = allowed == 1
        return allowed