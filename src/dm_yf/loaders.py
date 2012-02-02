# encoding=utf8
'''
Загрузчики данных.
@author: Mic, 2012
'''

from dm_yf.converters import AlbumConverter
from dm_yf.fotki import AlbumList 
from dm_yf.log import logger
from dm_yf.user import User

class AlbumListLoader(object):
    '''
    Загрузчик списка альбомов.
    '''

    def load(self):
        '''
        Загружает список альбомов.
        @return: AlbumList
        '''
        logger.info('loading album list')
        collection = User.get_album_collection()
        albums = map(AlbumConverter.from_entry, collection.get_entries())
        logger.info('album list loaded (%s)', len(albums))
        return AlbumList(albums)
