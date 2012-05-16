#!/usr/bin/python
# encoding=utf8
'''
Скрипт для проверки, есть ли доступ к аккаунту.
@author: Mic, 2012
'''

from dm_yf.log import logger
from dm_yf.models import AlbumList

album_list = AlbumList.get()
logger.info('now you have access to Fotki account')
logger.info('you have %s albums', len(album_list.albums))
