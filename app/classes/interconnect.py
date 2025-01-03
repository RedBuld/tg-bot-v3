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
                "Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiIxIiwianRpIjoiNWFlYmM5YTI4MmFkNDEyNzJhOTg5NmRjNTg5ZWYyOWVjMzUyZTI3NGJjNGEyMTFlYzQxZjkyMDZiNWQwNTZkZTg2YjNhYmMzNDQwNTVkNTUiLCJpYXQiOjE3MzUyNzU0NjEuNDg2NTg2LCJuYmYiOjE3MzUyNzU0NjEuNDg2NTg4LCJleHAiOjE3Mzc5NTM4NjEuNDgyOTQ3LCJzdWIiOiIyMjAxMjQwIiwic2NvcGVzIjpbXX0.bVA7fif8lN6sa1mXSRYJ16XoFl1MeuJYLtkU_eCR5hp9Mz7QSn4AoLBD_tj-XhD5YPjr_l4gEMrBkszcO9mhuM5Mw0UaBwfwLJtCLjOuE7dYPqBxZqrbffNNJB7U3C-1v_pDmHBtuoQqyCIAF8dxsRRqYCXBmdZvxbKRsjb92gCzFFzswf19RrzEvLTjZl19wx65vrlt_ADN_GEuUbhtkS0h_q5c1qwSskzzwLLABSKe4kLzjgn4llnTBufY1TKtYJD_yihKHKP221CvN-IXB5QWEfJaUb2eV6RFB05Mq1rqYlrrtJCAwMF1fYF3B_dDCuMAuwj4b_TcDJ8A40nzUhAa6-8zRwOqtXYNwLoymt2jplHLgA3NjAcZO4LRrUJ0JO6KgOIOt8ttz1uk7yjO7fWJ7NB-4qRvQQmoJh_aNa-FxH4ihkayV4hFgy4mIBa2sQzVGVkM8lNkRqgl8yzQaI5uL5lGmFPP57NZhasCT_hAymhD5JCU1A78SzNQEa0uxtNFn0Bl9hRCN6DX8OSPgygneZKoto9Hw0rVfE-TBjZXHHLxfXCaTnfOTWSdWmGKELxsnAe5VPrPkglmMx0xApr70_5W6D6rPHYdAKyhWyPf7WdCnmSi6z19smx8JhutgwYuJZo9Jckc8OmmYwGU_c-09-wRzZgbDy4ylMjR2Io"
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