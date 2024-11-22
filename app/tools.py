import re

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
    return site.encode().decode('idna')

def hideui(url: str) -> str:
    return re.sub(r"&?ui=\d+", "", url)