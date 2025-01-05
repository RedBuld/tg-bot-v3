from __future__ import annotations
import asyncio
import aiohttp
import ujson
import traceback
import logging
import urllib.parse
import hashlib
from aiohttp.client_exceptions import ClientError
from typing import List, Dict, Any
from app import variables
from app import dto
from app.configs import GC
from app.objects import RD

logger = logging.getLogger(__name__)

class Interconnect:

    @staticmethod
    async def GetSitesActive() -> List[ str ]:
        cache_key = variables.ACTIVE_SITES_CACHE_KEY
        model = dto.SitesListResponse()
        cached = await RD.get( cache_key )

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
            await RD.setex( cache_key, 60, cached )
        else:
            model = model.model_validate_json( cached )

        return model.sites

    @staticmethod
    async def GetSitesActiveGrouped() -> Dict[ str, List[ str ] ]:
        cache_key = variables.ACTIVE_SITES_CACHE_KEY
        model = dto.GroupedSitesResponse()
        cached = await RD.get( cache_key )

        if not cached:
            _attempts = 0
            while _attempts < 5:
                try:
                    async with aiohttp.ClientSession( json_serialize=ujson.dumps ) as session:
                        async with session.post( GC.queue_host + 'sites/active_grouped', verify_ssl=False ) as response:
                            if response.status == 200:
                                data = await response.json( loads=ujson.loads )
                                model = model.model_validate( data )
                                _attempts = 5
                except:
                    traceback.print_exc()
                    _attempts+=1
                    await asyncio.sleep(5)

            cached = model.model_dump_json()
            await RD.setex( cache_key, 60, cached )
        else:
            model = model.model_validate_json( cached )

        return model.groups

    @staticmethod
    async def GetSitesWithAuth() -> List[ str ]:
        cache_key = variables.AUTH_SITES_CACHE_KEY
        model = dto.SitesListResponse()
        cached = await RD.get( cache_key )

        if not cached:
            _attempts = 0
            while _attempts < 5:
                try:
                    async with aiohttp.ClientSession( json_serialize=ujson.dumps ) as session:
                        async with session.post( GC.queue_host + 'sites/auths', verify_ssl=False ) as response:
                            if response.status == 200:
                                data = await response.json( loads=ujson.loads )
                                logger.info( str(data) )
                                model = model.model_validate( data )
                                _attempts = 5
                except:
                    traceback.print_exc()
                    _attempts+=1
                    await asyncio.sleep(5)

            cached = model.model_dump_json()
            await RD.setex( cache_key, 60, cached )
        else:
            model = model.model_validate_json( cached )

        return model.sites

    @staticmethod
    async def GetSiteData( site_name: str ) -> dto.SiteCheckResponse:
        cache_key = f"cache_sites_data_{site_name}"
        model = dto.SiteCheckResponse()
        cached = await RD.get( cache_key )

        payload = dto.SiteCheckRequest( site=site_name ).model_dump( mode='json' )

        if not cached:
            _attempts = 0
            while _attempts < 5:
                try:
                    async with aiohttp.ClientSession( json_serialize=ujson.dumps ) as session:
                        async with session.post( GC.queue_host + 'sites/check', json=payload, verify_ssl=False ) as response:
                            if response.status == 200:
                                data = await response.json( loads=ujson.loads )
                                model = model.model_validate( data )
                                _attempts = 5
                except:
                    traceback.print_exc()
                    _attempts+=1
                    await asyncio.sleep(5)

            cached = model.model_dump_json()
            await RD.setex( cache_key, 60, cached )
        else:
            model = model.model_validate_json( cached )

        return model

    @staticmethod
    async def GetUsage( use_cache: bool = True ) -> Dict[ str, Any ]:
        cache_key = variables.USAGE_CACHE_KEY
        if use_cache:
            cached = await RD.get( cache_key )
        else:
            cached = None

        if not cached:
            stats = {}
            _attempts = 0
            while _attempts < 5:
                try:
                    async with aiohttp.ClientSession( json_serialize=ujson.dumps ) as session:
                        async with session.get( GC.queue_host + 'export/queue', verify_ssl=False ) as response:
                            if response.status == 200:
                                _attempts = 5
                                stats = await response.json( loads=ujson.loads )
                except:
                    _attempts+=1
                    await asyncio.sleep(1)
            
            cached = ujson.dumps( stats )
            await RD.setex( cache_key, 5, cached )
        else:
            stats = ujson.loads( cached )

        return stats

    @staticmethod
    async def GetStats() -> Dict[ str, Any ]:
        cache_key = variables.STATS_CACHE_KEY
        cached = await RD.get( cache_key )

        if not cached:
            stats = {}
            _attempts = 0
            while _attempts < 5:
                try:
                    async with aiohttp.ClientSession( json_serialize=ujson.dumps ) as session:
                        async with session.get( GC.queue_host + 'export/stats', verify_ssl=False ) as response:
                            if response.status == 200:
                                _attempts = 5
                                stats = await response.json( loads=ujson.loads )
                except:
                    _attempts+=1
                    await asyncio.sleep(1)
            
            cached = ujson.dumps( stats )
            await RD.setex( cache_key, 5, cached )
        else:
            stats = ujson.loads( cached )

        return stats
    

    ######################


    @staticmethod
    async def InitDownload( request: dto.DownloadRequest ) -> int | str:
        try:
            async with aiohttp.ClientSession( json_serialize=ujson.dumps ) as session:
                async with session.post( GC.queue_host + 'download/new', json=request.model_dump( mode='json' ), verify_ssl=False ) as response:
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
    async def CancelDownload( request: dto.DownloadCancelRequest ) -> dto.DownloadCancelResponse | str:
        try:
            async with aiohttp.ClientSession( json_serialize=ujson.dumps ) as session:
                async with session.post( GC.queue_host + 'download/cancel', json=request.model_dump( mode='json' ), verify_ssl=False ) as response:
                    if response.status == 200:
                        try:
                            data = await response.json( loads=ujson.loads )
                            return dto.DownloadCancelResponse.model_validate( data )
                        except:
                            return 'Загрузка не найдена'
                    else:
                        message = await response.json( loads=ujson.loads )
                        return message
        except ClientError as e:
            return "Ошибка соединения с сервером загрузки"
        except Exception as e:
            return str(e)


    @staticmethod
    async def ClearDownloadFiles( request: dto.DownloadClearRequest ) -> None:
        _attempts = 0
        while _attempts < 5:
            try:
                async with aiohttp.ClientSession( json_serialize=ujson.dumps ) as session:
                    async with session.post( GC.queue_host + 'download/clear', json=request.model_dump( mode='json' ), verify_ssl=False ) as response:
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
    async def AdminStopTasks() -> None:
        _attempts = 0
        while _attempts < 5:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post( GC.queue_host + 'queue/stop/tasks', verify_ssl=False ) as response:
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
    async def AdminStartTasks() -> None:
        _attempts = 0
        while _attempts < 5:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post( GC.queue_host + 'queue/start/tasks', verify_ssl=False ) as response:
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
    async def AdminStopResults() -> None:
        _attempts = 0
        while _attempts < 5:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post( GC.queue_host + 'queue/stop/results', verify_ssl=False ) as response:
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
    async def AdminStartResults() -> None:
        _attempts = 0
        while _attempts < 5:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post( GC.queue_host + 'queue/start/results', verify_ssl=False ) as response:
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
    async def AdminStopQueue() -> None:
        _attempts = 0
        while _attempts < 5:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post( GC.queue_host + 'queue/stop', verify_ssl=False ) as response:
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
    async def AdminStartQueue() -> None:
        _attempts = 0
        while _attempts < 5:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post( GC.queue_host + 'queue/start', verify_ssl=False ) as response:
                        if response.status == 200:
                            _attempts = 5
                        else:
                            _attempts+=1
                            await asyncio.sleep(5)
            except:
                traceback.print_exc()
                _attempts+=1
                await asyncio.sleep(5)


    ###


    @staticmethod
    async def CheckLink( link: str ) -> int:
        cache_key = "check_link_" + str( hashlib.md5( link.encode( 'utf-8' ) ).hexdigest() )
        allowed = await RD.get( cache_key )

        if allowed == None:
            allowed = variables.SiteAllowed.NO

            if 'lib.me/' in link:
                allowed = await Interconnect.checkLibMeSite( link )

            if 'tl.rulate.ru/' in link:
                allowed = await Interconnect.checkRulateSite( link )

            await RD.setex( cache_key, 86400, allowed )
        else:
            allowed = int( allowed )

        return allowed


    @staticmethod
    async def checkRulateSite( link: str ) -> int:
        return 1


    @staticmethod
    async def checkLibMeSite( link: str ) -> int:

        async def checkWithoutAuth( session: aiohttp.ClientSession, work: str, proxy ) -> bool:
            headers = {
                "Content-Type": "application/json"
            }

            async with session.get(
                f"https://api2.mangalib.me/api/manga/{work}?fields[]=background&fields[]=eng_name&fields[]=otherNames&fields[]=summary&fields[]=releaseDate&fields[]=type_id&fields[]=caution&fields[]=views&fields[]=close_view&fields[]=rate_avg&fields[]=rate&fields[]=genres&fields[]=tags&fields[]=teams&fields[]=user&fields[]=franchise&fields[]=authors&fields[]=publisher&fields[]=userRating&fields[]=moderated&fields[]=metadata&fields[]=metadata.count&fields[]=metadata.close_comments&fields[]=manga_status_id&fields[]=chap_count&fields[]=status_id&fields[]=artists&fields[]=format",
                headers=headers,
                verify_ssl=False,
                proxy=proxy
            ) as response:
                if response.status == 404:
                    return False
                else:
                    return True

        async def checkWithAuth( session: aiohttp.ClientSession, work: str, proxy: str ) -> bool:
            headers = {
                "Content-Type": "application/json",
                "Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiIxIiwianRpIjoiZjE0NmRhN2I5NzY0ODgyYzA3MWU2MzMyNzVlYTJiMDI2MmViODJiNWQwN2Y2YjdiYTQ1ZGY5NTllYzA1N2I3ZmY1MjlmY2YzNDVhNzI1NDAiLCJpYXQiOjE3MzUzNzY5NzguNDE1NDk4LCJuYmYiOjE3MzUzNzY5NzguNDE1NDk5LCJleHAiOjE3MzgwNTUzNzguNDEyMzM1LCJzdWIiOiIyMjAxMjQwIiwic2NvcGVzIjpbXX0.JR2vpghFZUvjK1AOhbVznN0yx3A607sd7snab-_PLte8bmdSu6bfUneA0pfi4WGpg-Lrz-_RMFrJCQsmjq5zrG5oBM5oOEcMC2VZyb8mmz0MW7b0Vbnk-TfDwl6pBdmKNAH_k8IOFSfcbbVJutV_BJ9VCB6LSAvSvLPAP4fG6HpWlKubxQoRy5a6ZTu3bxE6ZzDKCaHJhpZJw41yIuMfvigX1ETbSZSkuSOk_OxSH4BWyxnbmpWZgrQ26AZYxWbjApYlqwwUWyoILPnNWxxfRuSZvRPsSjKrEjgjbDAcVfTOjV8sXond-uvFkufoB8-smaMxFY2x7fWG8w5VsB8wLTOjpaqffyPxWvWCcMQpb1azkKDkDeehNGmvTnLHx7Ji7ilNoP7qqc2IEUHjekJMCnhMh4SoOMru9Z5VbGpD6qgK9nc1Cg5Qy8RQE__QKf9MSOYQGnIzlBrWcCYHeJo9Y0l6PxXKuAO7MMme-AqlEwV-Fhv_-R4qhO-U5qfW0mhiYX4NMyHeub60nJXoYSrLTA4Aa-_ESDcNYhfjTIDpmMZaW8CdM_95eJRUiIcKQoNfHMgOYquuvWldCcnBF7Gd9otmVJvMmMHX4AMu-cCy6zxivYbPGBvIao-ijXzMAJ403dbN1GyR8TAFDQ4LRLcqRclw2oD1NYMZV85S7BnCsbo"
            }

            async with session.get(
                f"https://api2.mangalib.me/api/manga/{work}?fields[]=background&fields[]=eng_name&fields[]=otherNames&fields[]=summary&fields[]=releaseDate&fields[]=type_id&fields[]=caution&fields[]=views&fields[]=close_view&fields[]=rate_avg&fields[]=rate&fields[]=genres&fields[]=tags&fields[]=teams&fields[]=user&fields[]=franchise&fields[]=authors&fields[]=publisher&fields[]=userRating&fields[]=moderated&fields[]=metadata&fields[]=metadata.count&fields[]=metadata.close_comments&fields[]=manga_status_id&fields[]=chap_count&fields[]=status_id&fields[]=artists&fields[]=format",
                headers=headers,
                verify_ssl=False,
                proxy=proxy
            ) as response:
                if response.status == 404:
                    return False
                else:
                    return True
        
        #
        
        allowed = variables.SiteAllowed.NO

        _data = link.split('/')

        domain = _data.pop( 2 )
        work = _data.pop( 4 )
        work = work.split( '?' ).pop( 0 )
        proxy = await GC.proxies.GetInstance( domain )

        async with aiohttp.ClientSession() as session:
            _attempts = 0
            while _attempts < 5:
                try:
                    allowed_without_auth = await checkWithoutAuth( session, work, proxy )
                    if allowed_without_auth:
                        allowed = variables.SiteAllowed.YES
                    else:
                        allowed_with_auth = await checkWithAuth( session, work, proxy )
                        if allowed_with_auth:
                            allowed = variables.SiteAllowed.AUTHED
                        else:
                            allowed = variables.SiteAllowed.NO
                    _attempts = 5
                except:
                    traceback.print_exc()
                    _attempts+=1
                    await asyncio.sleep(5)
            await session.close()
        
        return allowed