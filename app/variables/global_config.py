from __future__ import annotations
import os
import re
import ujson
from typing import List, Dict, Any

class GlobalConfig():
    bot_host:     str = 'http://bot:8000/'
    queue_host:   str = 'http://queue:8010/'
    redis_server: str = 'redis://redis:6379/1'
    # ENV based
    local_server: str | None = None
    url:          str = ''
    encrypt_key:  bytes | None = None
    # global.json based
    formats:      Dict[str,str] = {}
    groups:       Dict[str,str] = {}
    demo:         Dict[str,str] = {}
    admins:       List[int] = []
    proxies:      GlobalConfigProxies = None
    free_limit:   int = 100
    #
    mask:         re.Pattern = re.compile("https?:\\/\\/(www\\.|m\\.|ru\\.)*(?P<site>[^\\/]+)\\/.+")
    proxy:        re.Pattern = re.compile("(https?|socks[4,5]):\\/\\/\d{1,3}\\.\d{1,3}\\.\d{1,3}\\.\d{1,3}:\d{2,5}\\/")

    def __init__( self ):

        # ENV based settings

        local_server = os.environ.get('LOCAL_SERVER')
        if local_server:
            self.local_server = f'http://{local_server}:8081'


        url = os.environ.get('URL')
        if url:
            self.url = bytes(url, encoding='utf-8')


        encrypt_key = os.environ.get('ENCRYPT_KEY')
        if encrypt_key:
            self.encrypt_key = bytes(encrypt_key, encoding='utf-8')
        else:
            if url:
                raise Exception('Set ENCRYPT_KEY environment variable, use https://fernetkeygen.com/ for generating')

        # global.json based settings

        config_file = '/app/configs/global.json'
        if not os.path.exists(config_file):
            raise FileNotFoundError(config_file)


        config: Dict[str,Any] = {}
        with open( config_file, 'r', encoding='utf-8' ) as _config_file:
            _config = _config_file.read()
            config = ujson.loads( _config )


        if 'formats' in config:
            self.formats = config['formats']
        else:
            self.formats = {
                "fb2": "Fb2 - для книг",
                "mp3": "mp3 - для аудиокниг",
                "epub": "Epub - для книг",
                "cbz": "CBZ - для манги"
            }


        if 'admins' in config:
            self.admins = config['admins']
        else:
            self.admins = []


        if 'groups' in config:
            self.groups = config['groups']
        else:
            self.groups = {}


        if 'demo' in config:
            self.demo = config['demo']
        else:
            self.demo = {}


        if 'free_limit' in config:
            self.free_limit = config['free_limit']
        else:
            self.free_limit = 100


        _proxies = []
        if 'proxies' in config:
            _proxies = config['proxies']
        if self.proxies is None:
            self.proxies = GlobalConfigProxies()
            self.proxies.instances = _proxies


    async def UpdateConfig( self ):
        self.__init__()


class GlobalConfigProxies():
    instances: List[ str ]         = []
    last_by_site: Dict[ str, int ] = {}

    def __init__(
        self,
        instances: List[ str ] = [],
        last_by_site: Dict[ str, int ] = {}
    ) -> None:
        self.instances    = instances
        self.last_by_site = last_by_site


    def Has( self ) -> bool:
        return len( self.instances ) != 0


    async def GetInstance(
        self,
        site: str,
        exclude: List[ str ] = []
    ) -> str:
        index = 0

        instances = list( set( self.instances ) - set( exclude ) )

        if len( instances ) == 0:
            return ''

        if site in self.last_by_site:
            index = self.last_by_site[ site ]
            index += 1
            if index > len( instances ) - 1:
                index = 0

        self.last_by_site[ site ] = index
        return instances[ index ]