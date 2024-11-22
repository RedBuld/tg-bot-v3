import traceback
import os
import logging
import ujson
import asyncio
from typing import List, Dict, Any
from datetime import datetime
from sqlalchemy import func, select, delete, exists, or_, and_
from sqlalchemy import create_engine
from sqlalchemy import Engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session
from sqlalchemy.exc import *
from sqlalchemy.dialects.mysql import insert
from app import variables
from app import models

logger = logging.getLogger(__name__)

class DataBase(object):
    _engine: Engine
    _session: sessionmaker[Session]

    __server: str = ""

    def __init__(self):
        self._engine = None
        self._session = None
        return
    
    async def Start(self) -> None:
        if self._engine:
            return

        while True:
            try:
                if not self._engine:
                    self._engine = create_engine(
                        self.__server,
                        pool_size=5, max_overflow=5, pool_recycle=60, pool_pre_ping=True
                    )
                    self._session = sessionmaker(self._engine, expire_on_commit=False)

                await self.createDB()
                logger.info('DB: started')
                return
            except:
                await asyncio.sleep(1)
                continue
    
    async def Stop(self) -> None:
        if self._engine:
            logger.info('DB: finished')
            self._engine.dispose()
            self._engine = None
            self._session = None

    async def createDB(self) -> None:
        if self._engine:
            logger.info('DB: validate database')
            models.Base.metadata.create_all( bind=self._engine, checkfirst=True )
            logger.info('DB: validated database')
    
    async def updateConfig(self) -> None:

        config_path = []

        cwd = os.getcwd()

        config_path.append(cwd)

        if not cwd.endswith('app/') and not cwd.endswith('app'):
            config_path.append('app')

        config_file = os.path.join( *config_path, 'configs', 'database.json' )

        config: Dict[str,Any] = {}

        try:
            if not os.path.exists(config_file):
                raise FileNotFoundError(config_file)

            with open( config_file, 'r', encoding='utf-8' ) as _config_file:
                _config = _config_file.read()
                config = ujson.loads( _config )
        except:
            traceback.print_exc()

        self.__server = config['server'] if 'server' in config else ""

        if self._engine:
            await self.Stop()
            await self.Start()

    async def saveUser(
        self,
        user: models.User
    ) -> models.User:
        session = self._session()
        try:
            session.add(user)
            session.commit()
            session.flush()
            session.close()
            return user
        except OperationalError as e:
            await asyncio.sleep(1)
            return await self.saveUser( user=user )
        except Exception as e:
            raise e
        finally:
            session.close()

    async def getUser(
        self,
        user_id: int
    ) -> models.User|None:
        session = self._session()
        try:
            query = session.execute(
                select(models.User)\
                .where(
                    models.User.id==user_id
                )
            )
            result = query.scalar_one_or_none()
            session.close()
            if not result:
                return None
            return result
        except OperationalError as e:
            await asyncio.sleep(1)
            return await self.getUser( user_id=user_id )
        except Exception as e:
            raise e
        finally:
            session.close()

    async def getUserSetuped(
        self,
        user_id: int
    ) -> int:
        session = self._session()
        try:
            query = session.execute(
                select(models.User.setuped)\
                .where(
                    models.User.id==user_id
                )
            )
            result = query.scalar_one_or_none()
            session.close()
            return result == 1
        except OperationalError as e:
            await asyncio.sleep(1)
            return await self.getUserSetuped( user_id=user_id )
        except Exception as e:
            raise e
        finally:
            session.close()

    async def getUserInteractMode(
        self,
        user_id: int
    ) -> int:
        session = self._session()
        try:
            query = session.execute(
                select(models.User.interact_mode)
                .where(
                    models.User.id==user_id
                )
            )
            result = query.scalar_one_or_none()
            session.close()
            return result == 1
        except OperationalError as e:
            await asyncio.sleep(1)
            return await self.getUserInteractMode( user_id=user_id )
        except Exception as e:
            raise e
        finally:
            session.close()
    
    async def getUserAuthedSites(
        self,
        user_id: int
    ) -> List[ models.UserAuth ]:
        session = self._session()
        try:
            query = session.execute(
                select(models.UserAuth.site)\
                .distinct()\
                .where(
                    models.UserAuth.user_id==user_id
                )
            )
            result = query.scalars().all()
            session.close()
            return result
        except OperationalError as e:
            await asyncio.sleep(1)
            return await self.getUserAuthedSites( user_id=user_id )
        except Exception as e:
            raise e
        finally:
            session.close()

    async def getUserAuthsForSite(
        self,
        user_id: int,
        site: str
    ) -> List[ models.UserAuth ]:
        session = self._session()
        try:
            query = session.execute(
                select(models.UserAuth)\
                .where(
                    models.UserAuth.user_id==user_id,
                    models.UserAuth.site==site
                )
            )
            result = query.scalars().all()
            session.close()
            return result
        except OperationalError as e:
            await asyncio.sleep(1)
            return await self.getUserAuthsForSite( user_id=user_id, site=site )
        except Exception as e:
            raise e
        finally:
            session.close()

    async def saveUserAuth(
        self,
        user_id: int,
        site: str,
        login: str,
        password: str
    ) -> models.UserAuth:
        session = self._session()
        try:
            auth = models.UserAuth()
            auth.user_id = user_id
            auth.site = site
            auth.login = login
            auth.password = password
            session.add(auth)
            session.commit()
            session.flush()
            session.close()
            return auth
        except OperationalError as e:
            await asyncio.sleep(1)
            return await self.saveUserAuth( user_id=user_id, site=site, login=login, password=password )
        except Exception as e:
            raise e
        finally:
            session.close()

    async def deleteUserAuth(
        self,
        user_id: int,
        auth_id: int
        ) -> None:
        session = self._session()
        try:
            session.execute(
                delete(models.UserAuth)\
                    .where(
                        models.UserAuth.user_id==user_id,
                        models.UserAuth.id==auth_id
                    )
                )
            session.commit()
            session.flush()
            session.close()
        except OperationalError as e:
            await asyncio.sleep(1)
            return await self.deleteUserAuth( user_id, user_id=user_id, auth_id=auth_id )
        except Exception as e:
            raise e
        finally:
            session.close()

    async def getUserAuth(
        self,
        user_id: int,
        auth_id: int
    ) -> models.UserAuth:
        session = self._session()
        try:
            query = session.execute(
                select(models.UserAuth)\
                .where(
                    models.UserAuth.user_id==user_id,
                    models.UserAuth.id==auth_id)
                )
            result = query.scalar_one_or_none()
            session.close()
            return result
        except OperationalError as e:
            await asyncio.sleep(1)
            return await self.getUserAuth( user_id=user_id, auth_id=auth_id )
        except Exception as e:
            raise e
        finally:
            session.close()

    async def getUserUsage(
        self,
        user_id: int
    ) -> int:
        return 0

    #

    async def UpdateUserStat(self, result: dict) -> None:

        if result['status'] == variables.DownloaderStep.CANCELLED:
            return

        success = 1 if result['status'] == variables.DownloaderStep.DONE else 0
        failure = 1 if result['status'] == variables.DownloaderStep.ERROR else 0

        session = self._session()
        try:
            ss = {
                'user_id': result['user_id'],
                'site': result['site'],
                'day': datetime.today(),
                'success': success,
                'failure': failure,
                'orig_size': result['orig_size'],
                'oper_size': result['oper_size'],
            }
            session.execute(
                insert(models.UserStat)\
                .values(**ss)\
                .on_duplicate_key_update(
                    success=models.UserStat.success + success,
                    failure=models.UserStat.failure + failure,
                    orig_size=models.UserStat.orig_size + result['orig_size'],
                    oper_size=models.UserStat.oper_size + result['oper_size'],
                )
            )
            session.commit()
            session.close()
        except OperationalError as e:
            await asyncio.sleep(1)
            return await self.UpdateUserStat(result)
        except Exception as e:
            raise e
        finally:
            session.close()
    
    async def saveInlineDownloadRequest(
        self,
        request: models.InlineDownloadRequest
    ) -> models.InlineDownloadRequest:
        session = self._session()
        try:
            session.add(request)
            session.commit()
            session.flush()
            session.close()
            return request
        except OperationalError as e:
            await asyncio.sleep(1)
            return await self.saveInlineDownloadRequest( request=request )
        except Exception as e:
            raise e
        finally:
            session.close()
    
    async def getInlineDownloadRequest(
        self,
        bot_id: str,
        user_id: int,
        chat_id: int,
        message_id: int
    ) -> models.InlineDownloadRequest | None:
        session = self._session()
        try:
            query = session.execute(
                select(models.InlineDownloadRequest)\
                    .where(
                        models.InlineDownloadRequest.bot_id==bot_id,
                        models.InlineDownloadRequest.user_id==user_id,
                        models.InlineDownloadRequest.chat_id==chat_id,
                        models.InlineDownloadRequest.message_id==message_id
                    )
                )
            result = query.scalar_one_or_none()
            session.close()
            if not result:
                return None
            return result
        except OperationalError as e:
            await asyncio.sleep(1)
            return await self.getInlineDownloadRequest( bot_id=bot_id, user_id=user_id, chat_id=chat_id, message_id=message_id )
        except Exception as e:
            raise e
        finally:
            session.close()

    async def deleteInlineDownloadRequest(
        self,
        bot_id: str,
        user_id: int,
        chat_id: int,
        message_id: int
    ) -> None:
        session = self._session()
        try:
            session.execute(
                delete(models.InlineDownloadRequest)\
                    .where(
                        models.InlineDownloadRequest.bot_id==bot_id,
                        models.InlineDownloadRequest.user_id==user_id,
                        models.InlineDownloadRequest.chat_id==chat_id,
                        models.InlineDownloadRequest.message_id==message_id
                    )
                )
            session.commit()
            session.flush()
            session.close()
        except OperationalError as e:
            await asyncio.sleep(1)
            return await self.deleteInlineDownloadRequest( bot_id=bot_id, user_id=user_id, chat_id=chat_id, message_id=message_id )
        except Exception as e:
            raise e
        finally:
            session.close()