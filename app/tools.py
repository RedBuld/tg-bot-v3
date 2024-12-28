import os
import re
import json
import asyncio
from typing import Any, Dict
from aiogram.fsm.context import FSMContext

def prettyJSON(data: Dict) -> str:
    return json.dumps(data, ensure_ascii=False, indent=4)

def humanizeChapters( start: int, end: int ) -> str:
    res = ''
    if start and end:
        res = f'с {start} до {end}'
    elif start and not end:
        if start > 0:
            res = f'с {start}'
        else:
            if start == -1:
                res = f'последнюю'
            else:
                res = f'последние {abs( start )}'
    elif end and not start:
        if end > 0:
            res = f'до {end}'
        else:
            if end == -1:
                res = f'без последней'
            else:
                res = f'без последних {abs( end )}'
    return res

def humanizeSize(size: int) -> str:
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

def punyDecode(string: str) -> str:
    try:
        return string.encode().decode('idna')
    except:
        return string

def hideUI(url: str) -> str:
    return re.sub(r"&?ui=\d+", "", url)

def yesOrNo( value: Any, check: Any ) -> str:
    return '🗹' if value == check else '☐'

def cleanFilename( filename: str ) -> str:
    from unicodedata import normalize
    _filename_ascii_strip_re = re.compile(r'[^\w\d\.\,\-\_\[\]\{\}\s\#\№\:\!]')
    filename = normalize('NFKD', filename).encode('ascii', 'ignore').decode('ascii')
    for sep in [os.path.sep, os.path.altsep]:
        if sep:
            filename = filename.replace(sep, '')
    filename = _filename_ascii_strip_re.sub( '', filename ).strip('_').strip('.').strip()
    filename = re.sub(r'\s+',' ', filename)
    return filename

async def stateChecker( state: FSMContext ) -> str | None:
    actual_state = await state.get_state()

    if actual_state:
        if actual_state.startswith( 'AuthForm' ):
            return "Отмените или завершите предыдущую авторизацию"
        elif actual_state.startswith( 'SetupAccount' ):
            return "Отмените или завершите настройку аккаунта"
        elif actual_state.startswith( 'SetupSite' ):
            return "Отмените или завершите настройку сайта"
        elif actual_state.startswith( 'InlineDownload' ):
            return "Отмените или завершите настройку загрузки"
        else:
            return "Отмените или завершите другое действие"
    return None
    