from __future__ import annotations

import os
from typing import List, Dict
from pydantic import BaseModel

class AuthSetupRequest(BaseModel):
    user_id:    int
    chat_id:    int
    message_id: int
    site:       str
    login:      str
    password:   str

class SiteCheckRequest(BaseModel):
    site:       str

class SiteCheckResponse(BaseModel):
    allowed:    bool = False
    parameters: List[ str ] = []
    formats:    Dict[ str, List[ str ] ] = {}

class SiteListResponse(BaseModel):
    sites:      List[ str ] = []

class DownloadSetupRequest(BaseModel):
    user_id:    int
    chat_id:    int
    message_id: int
    format:     str
    link:       str
    site:       str
    auth:       str | None = None
    start:      int | None = 0
    end:        int | None = 0
    cover:      bool | None = False
    images:     bool | None = False
    proxy:      str | None = ''
    hashtags:   str | None = 'no'
    filename:   str | None = None

class DownloadRequest(BaseModel):
    task_id:    int | None = None
    user_id:    int
    web_id:     str | None = None
    chat_id:    int
    message_id: int
    site:       str
    url:        str
    start:      int | None = 0
    end:        int | None = 0
    format:     str | None = "fb2"
    login:      str | None = ""
    password:   str | None = ""
    images:     bool | None = False
    cover:      bool | None = False
    proxy:      str | None = ""
    hashtags:   str | None = "no"
    filename:   str | None = None

    class Config:
        from_attributes = True

class DownloadCancelRequest(BaseModel):
    task_id:    int

class DownloadCancelResponse(BaseModel):
    user_id:    int
    web_id:     str | None = None
    chat_id:    int
    message_id: int

class DownloadClearRequest(BaseModel):
    task_id:    int

class DownloadResult(BaseModel):
    task_id:    int
    user_id:    int
    web_id:     str | None = None
    chat_id:    int
    message_id: int
    site:       str
    proxy:      str | None = ""
    status:     int
    text:       str
    cover:      str | os.PathLike
    files:      List[ str | os.PathLike ]
    orig_size:  int
    oper_size:  int

    class Config:
        from_attributes = True

class DownloadStatus(BaseModel):
    task_id:    int
    user_id:    int
    web_id:     str | None = None
    chat_id:    int
    message_id: int
    text:       str
    status:     int
