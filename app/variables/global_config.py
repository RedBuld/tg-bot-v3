import os
import re
import ujson
import traceback
from typing import List, Dict, Any

class GlobalConfig():
    bot_id:      str
    bot_host:    str
    queue_host:  str
    free_limit:  int = 100
    formats:     Dict[str,str] = {}
    groups:      Dict[str,str] = {}
    demo:        Dict[str,str] = {}
    admins:      List[int] = []
    encrypt_key: bytes
    mask:        re.Pattern = re.compile("https?:\\/\\/(www\\.|m\\.|ru\\.)*(?P<site>[^\\/]+)\\/.+")
    inited:      bool = False

    # def __escape_md__( self, text: str ) -> str:
    #     text = text\
    #         .replace('_', '\\_')\
    #         .replace('*', '\\*')\
    #         .replace('[', '\\[')\
    #         .replace(']', '\\]')\
    #         .replace('(', '\\(')\
    #         .replace(')', '\\)')\
    #         .replace('~', '\\~')\
    #         .replace('`', '\\`')\
    #         .replace('>', '\\>')\
    #         .replace('#', '\\#')\
    #         .replace('+', '\\+')\
    #         .replace('-', '\\-')\
    #         .replace('=', '\\=')\
    #         .replace('|', '\\|')\
    #         .replace('{', '\\{')\
    #         .replace('}', '\\}')\
    #         .replace('.', '\\.')\
    #         .replace('!', '\\!')
    #     return text

    async def updateConfig( self ):
        config_path = []

        cwd = os.getcwd()

        config_path.append(cwd)

        if not cwd.endswith('app/') and not cwd.endswith('app'):
            config_path.append('app')

        config_file = os.path.join( *config_path, 'configs', 'global.json' )

        config: Dict[str,Any] = {}

        try:
            if not os.path.exists(config_file):
                raise FileNotFoundError(config_file)

            with open( config_file, 'r', encoding='utf-8' ) as _config_file:
                _config = _config_file.read()
                config = ujson.loads( _config )
        except Exception as e:
            if not self.inited:
                raise e
            traceback.print_exc()
        
        if 'queue_host' in config:
            self.queue_host = config['queue_host']
        else:
            raise Exception('No queue_host defined')

        if 'encrypt_key' in config:
            self.encrypt_key = bytes(config['encrypt_key'], encoding='utf-8')
        else:
            raise Exception('No encrypt_key defined')
        
        if 'formats' in config:
            self.formats = config['formats']
        else:
            raise Exception('No formats defined')

        if 'admins' in config:
            self.admins = config['admins']
        else:
            raise Exception('No admins defined')
        
        if 'bot_id' in config:
            self.bot_id = config['bot_id']
        else:
            raise Exception('No bot_id defined')

        if 'bot_host' in config:
            self.bot_host = config['bot_host']
        else:
            self.bot_host = ''
        
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