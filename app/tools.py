import os
import re
import json
import asyncio
from typing import Any, Dict

def pretty_json(data: Dict) -> str:
    return json.dumps(data, ensure_ascii=False, indent=4)

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
    try:
        return site.encode().decode('idna')
    except:
        return site

def hideui(url: str) -> str:
    return re.sub(r"&?ui=\d+", "", url)

def yes_no( value: Any, check: Any ) -> str:
    return '🗹' if value == check else '☐'

def clean_filename( filename: str ) -> str:
    from unicodedata import normalize
    _filename_ascii_strip_re = re.compile(r'[^\w\d\.\-\_\[\]\{\}\s]')
    filename = normalize('NFKD', filename).encode('ascii', 'ignore').decode('ascii')
    for sep in [os.path.sep, os.path.altsep]:
        if sep:
            filename = filename.replace(sep, '')
    filename = _filename_ascii_strip_re.sub( '', filename ).strip('_').strip('.').strip()
    filename = re.sub(r'\s+',' ', filename)
    return filename