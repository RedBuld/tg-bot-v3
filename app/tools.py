import re
import json
import asyncio

def pretty_json(data: dict) -> str:
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

async def autoclean() -> None:
    from app.handlers.downloads.inline import InlineDownloadsController
    asyncio.create_task( InlineDownloadsController.clear_abandoned() )