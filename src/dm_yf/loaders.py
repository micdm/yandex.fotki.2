# encoding=utf8
'''
Загрузчики данных.
@author: Mic, 2012
'''

from dm_yf.atompub import Collection
from dm_yf.converters import AlbumConverter, PhotoConverter
from dm_yf.log import logger
from dm_yf.user import User
import dm_yf.utils as utils

class AlbumListLoader(object):
    '''
    Загрузчик списка альбомов.
    '''

    @classmethod
    def load(cls):
        '''
        Загружает список альбомов.
        @return: list
        '''
        logger.info('loading album list')
        collection = User.get_album_collection()
        albums = map(AlbumConverter.from_entry, collection.get_entries())
        logger.info('album list loaded (%s)', len(albums))
        return albums


class PhotoListLoader(object):
    '''
    Загрузчик списка фотографий.
    '''
    
    @classmethod
    def load(cls, album):
        '''
        Загружает список фотографий.
        @param album: Album
        @return: list
        '''
        logger.info('loading photo list for album %s', album)
        collection = User.get_album_collection()
        entry = utils.get_album_entry(collection, album)
        collection = Collection.load(entry.get_url('photos'))
        photos = map(PhotoConverter.from_entry, collection.get_entries())
        logger.info('photo list loaded for album %s (%s)', album, len(photos))
        return photos
