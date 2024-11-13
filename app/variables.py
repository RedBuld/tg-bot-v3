# -*- coding: utf-8 -*-
# pylint: disable=C0103,R0903
from __future__ import annotations
from dataclasses import dataclass, field

import os
import logging
import ujson
import traceback
from datetime import datetime, timedelta
from multiprocessing import Process
from typing import List, Dict
from aiogram import Bot as aiogramBot
from aiogram.fsm.state import State, StatesGroup

logger = logging.getLogger(__name__)

####

class AuthForm(StatesGroup):
    base_message = State()
    last_message = State()
    site = State()
    login = State()
    password = State()

class InlineDownloadForm(StatesGroup):
    base_message = State()
    last_message = State()
    start_page = State()
    end_page = State()

####

class GlobalConfig():
    bot_host:    str
    queue_host:  str
    free_limit:  int = 10
    formats:     Dict[str,str] = field(default_factory=dict)
    demo:        Dict[str,str] = field(default_factory=dict)
    encrypt_key: bytes


    def __escape_md__( self, text: str ) -> str:
        text = text\
            .replace('_', '\\_')\
            .replace('*', '\\*')\
            .replace('[', '\\[')\
            .replace(']', '\\]')\
            .replace('(', '\\(')\
            .replace(')', '\\)')\
            .replace('~', '\\~')\
            .replace('`', '\\`')\
            .replace('>', '\\>')\
            .replace('#', '\\#')\
            .replace('+', '\\+')\
            .replace('-', '\\-')\
            .replace('=', '\\=')\
            .replace('|', '\\|')\
            .replace('{', '\\{')\
            .replace('}', '\\}')\
            .replace('.', '\\.')\
            .replace('!', '\\!')
        return text
    async def updateConfig(
        self
    ):
        database_config_file = os.path.join( os.path.dirname( __file__ ), 'configs', 'global.json' )

        config = None

        try:
            if not os.path.exists(database_config_file):
                raise FileNotFoundError(database_config_file)

            with open( database_config_file, 'r', encoding='utf-8' ) as _config_file:
                _config = _config_file.read()
                config = ujson.loads( _config )
        except:
            traceback.print_exc()

        self.bot_host = config['bot_host'] if 'bot_host' in config else None
        
        self.queue_host = config['queue_host'] if 'queue_host' in config else None
        
        self.free_limit = config['free_limit'] if 'free_limit' in config else None
        
        self.formats = config['formats'] if 'formats' in config else None
        
        self.demo = config['demo'] if 'demo' in config else None

        if 'encrypt_key' in config:
            self.encrypt_key = bytes(config['encrypt_key'], encoding='utf-8')
        else:
            raise Exception('No encrypt_key defined')

####

@dataclass(frozen=True)
class DownloaderStep():
    CANCELLED: int = 99
    ERROR: int = 98
    IDLE: int = 0
    WAIT: int = 1
    INIT: int = 2
    RUNNING: int = 3
    PROCESSING: int = 4
    DONE: int = 5


@dataclass(frozen=True)
class InteractionModes():
    inline: str = "В чате"
    windowed: str = "Отдельные окна"