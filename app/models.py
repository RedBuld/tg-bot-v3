from typing import Self
from datetime import datetime
from sqlalchemy import Integer, BigInteger, Boolean, String, Text, UniqueConstraint, Date, DateTime, ForeignKey
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import Mapped
from sqlalchemy.dialects.mysql import ENUM

from app import dto

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] =              mapped_column( 'id', BigInteger, primary_key=True )
    username: Mapped[str] =        mapped_column( 'username', String(100), nullable=False )
    setuped: Mapped[bool] =        mapped_column( 'setuped', Boolean, default=False )
    ask_share: Mapped[bool] =      mapped_column( 'ask_share', Boolean, default=True )
    interact_mode: Mapped[int] =   mapped_column( 'interact_mode', Integer, default=0 )
    cover: Mapped[bool] =          mapped_column( 'cover', Boolean, default=True )
    thumb: Mapped[bool] =          mapped_column( 'thumb', Boolean, default=True )
    images: Mapped[bool] =         mapped_column( 'images', Boolean, default=True )
    format: Mapped[str] =          mapped_column( 'format', String(20), default='fb2' )
    hashtags: Mapped[str] =        mapped_column( 'hashtags', String(5), default='no' )
    filename: Mapped[str] =        mapped_column( 'filename', Text, nullable=True )

class UserStat(Base):
    __tablename__ = 'users_stats'
    __table_args__ = ( UniqueConstraint("user_id", "site", "day", name="user_site_day_index"), )

    id: Mapped[int] =              mapped_column( 'id', BigInteger, primary_key=True )
    user_id: Mapped[int] =         mapped_column( 'user_id', BigInteger, nullable=False, index=True )
    site: Mapped[str] =            mapped_column( 'site', String(100), nullable=False )
    day: Mapped[datetime] =        mapped_column( 'day', Date, default=datetime.today )
    success: Mapped[int] =         mapped_column( 'success', BigInteger, default=1 )
    failure: Mapped[int] =         mapped_column( 'failure', BigInteger, default=1 )
    orig_size: Mapped[int] =       mapped_column( 'orig_size', BigInteger, default=0 )
    oper_size: Mapped[int] =       mapped_column( 'oper_size', BigInteger, default=0 )

class UserAuth(Base):
    __tablename__ = 'users_auths'

    id: Mapped[int] =              mapped_column( 'id', BigInteger, primary_key=True )
    user_id: Mapped[int] =         mapped_column( 'user_id', BigInteger, nullable=False, index=True )
    site: Mapped[str] =            mapped_column( 'site', String(240), nullable=False, index=True )
    login: Mapped[str] =           mapped_column( 'login', Text, nullable=True )
    password: Mapped[str] =        mapped_column( 'password', Text, nullable=True )
    created_on: Mapped[datetime] = mapped_column( 'created_on', Date, default=datetime.today )

    def get_name(self):
        _r = self.login
        if self.created_on:
            _r = _r+' [от '+str(self.created_on.strftime('%d.%m.%Y'))+']'
        return _r

class InlineDownloadRequest(Base):
    __tablename__ = 'inline_download_requests'

    id: Mapped[int] =              mapped_column( 'id', BigInteger, primary_key=True )
    user_id: Mapped[int] =         mapped_column( 'user_id', BigInteger, nullable=False, index=True )
    chat_id: Mapped[int] =         mapped_column( 'chat_id', BigInteger, nullable=False, index=True )
    message_id: Mapped[int] =      mapped_column( 'message_id', BigInteger, nullable=True, index=True )
    setup_mode: Mapped[int] =      mapped_column( 'setup_mode', Integer, default=0)
    # 
    use_paging: Mapped[bool] =     mapped_column( 'use_paging', Boolean, default=False )
    use_auth: Mapped[bool] =       mapped_column( 'use_auth', Boolean, default=False )
    use_images: Mapped[bool] =     mapped_column( 'use_images', Boolean, default=False )
    use_cover: Mapped[bool] =      mapped_column( 'use_cover', Boolean, default=False )
    force_images: Mapped[bool] =   mapped_column( 'force_images', Boolean, default=False )
    force_auth: Mapped[bool] =     mapped_column( 'force_auth', Boolean, default=False )
    # 
    link: Mapped[str] =            mapped_column( 'link', Text, default='')
    site: Mapped[str] =            mapped_column( 'site', Text, default='')
    metasite: Mapped[str] =        mapped_column( 'metasite', Text, default='')
    auth: Mapped[str] =            mapped_column( 'auth', Text, default='')
    start: Mapped[int] =           mapped_column( 'start', Integer, default=0 )
    end: Mapped[int] =             mapped_column( 'end', Integer, default=0 )
    format: Mapped[str] =          mapped_column( 'format', Text, default='')
    images: Mapped[bool] =         mapped_column( 'images', Boolean, default=True )
    cover: Mapped[bool] =          mapped_column( 'cover', Boolean, default=True )
    thumb: Mapped[bool] =          mapped_column( 'thumb', Boolean, default=True )
    proxy: Mapped[str] =           mapped_column( 'proxy', Text, nullable=True )
    hashtags: Mapped[str] =        mapped_column( 'hashtags', String(10), default='no' )
    filename: Mapped[str] =        mapped_column( 'filename', Text, nullable=True )
    #
    created: Mapped[datetime] =    mapped_column( 'created', DateTime, default=datetime.now )


class ACL(Base):
    __tablename__ = 'acl'

    user_id: Mapped[int] =         mapped_column( 'user_id', BigInteger, primary_key=True, nullable=False, index=True )
    premium: Mapped[bool] =        mapped_column( 'premium', Boolean, default=False )
    p_type: Mapped[str] =          mapped_column( 'p_type', ENUM('usage','limit') )
    p_limit: Mapped[int] =         mapped_column( 'p_limit', Text )
    p_reason: Mapped[str] =        mapped_column( 'p_reason', Text )
    p_until: Mapped[datetime] =    mapped_column( 'p_until', DateTime, default=datetime.now )
    banned: Mapped[bool] =         mapped_column( 'banned', Boolean, default=False )
    b_type: Mapped[str] =          mapped_column( 'b_type', ENUM('usage','limit') )
    b_reason: Mapped[str] =        mapped_column( 'b_reason', Text )
    b_limit: Mapped[int] =         mapped_column( 'b_limit', Text )
    b_until: Mapped[datetime] =    mapped_column( 'b_until', DateTime, default=datetime.now )

    def getLimit( self ):
        if self.banned:
            if self.b_until < datetime.now():
                return None
            if self.b_type == 'usage':
                return -1
            if self.b_type == 'limit':
                return self.b_limit
        if self.premium:
            if self.p_until < datetime.now():
                return None
            if self.p_type == 'usage':
                return 1000
            if self.p_type == 'limit':
                return self.p_limit


class SiteConfig(Base):
    __tablename__ = 'sites_configs'

    id: Mapped[int] =              mapped_column( 'id', BigInteger, primary_key=True )
    user_id: Mapped[int] =         mapped_column( 'user_id', BigInteger, nullable=False, index=True )
    site: Mapped[str] =            mapped_column( 'site', Text, default='')
    #
    cover: Mapped[bool] =          mapped_column( 'cover', Boolean, nullable=True )
    thumb: Mapped[bool] =          mapped_column( 'thumb', Boolean, nullable=True )
    images: Mapped[bool] =         mapped_column( 'images', Boolean, nullable=True )
    auth: Mapped[str] =            mapped_column( 'auth', String(20), nullable=True )
    format: Mapped[str] =          mapped_column( 'format', String(20), nullable=True )
    proxy: Mapped[str] =           mapped_column( 'proxy', Text, nullable=True )
    hashtags: Mapped[str] =        mapped_column( 'hashtags', String(5), nullable=True )
    filename: Mapped[str] =        mapped_column( 'filename', Text, nullable=True )

    def __repr__( self ) -> str:
        return str({
            'user_id': self.user_id,
            'site': self.site,
            'cover': self.cover,
            'thumb': self.thumb,
            'images': self.images,
            'auth': self.auth,
            'format': self.format,
            'proxy': self.proxy,
            'hashtags': self.hashtags,
            'filename': self.filename,
        })