# encoding=utf8
'''
Классы для сохранения данных.
@author: Mic, 2012
'''

from xml.etree.ElementTree import tostring, Element, TreeBuilder

from dm_yf.atompub import ATOM_NS
from dm_yf.fotki import Album
from dm_yf.log import logger
from dm_yf.http import HttpClient

class AlbumListStore(object):
    '''
    Сохранение списка альбомов.
    '''
    
    def __init__(self, album_list):
        '''
        @param album_list: AlbumList
        '''
        self._http_client = HttpClient()
        self._album_list = album_list
        
    def _get_node_from_album(self, album):
        '''
        Создает XML-ноду на основе альбома.
        @param album: Album
        @return: Element
        '''
        builder = TreeBuilder(Element)
        builder.start('entry', {'xmlns': ATOM_NS})
        builder.start('title', {})
        builder.data(album.get_title())
        builder.end('title')
        builder.end('entry')
        return builder.close()
    
    def _add_album(self, album):
        '''
        Создает альбом.
        @param album: Album
        '''
        logger.debug('album %s is new, creating', album)
        node = self._get_node_from_album(album)
        collection = self._album_list.get_collection()
        collection.add_entry(node)
        album.set_state(Album.STATE_SYNCED)
    
    def _delete_album(self, album):
        '''
        Удаляет альбом.
        @param album: Album
        '''
        raise NotImplementedError()
    
    def _store_album(self, album):
        '''
        Сохраняет альбом.
        @param album: Album
        '''
        logger.debug('storing album %s', album)
        state = album.get_state()
        if state == Album.STATE_NEW:
            self._add_album(album)
        if state == Album.STATE_SYNCED:
            logger.debug('album %s is already synced, skipping', album)
        if state == Album.STATE_DELETED:
            self._delete_album(album)
    
    def store(self):
        '''
        Сохраняет список альбомов.
        @param album_list: AlbumList
        '''
        logger.info('storing album list')
        albums = self._album_list.get_albums()
        for album in albums:
            self._store_album(album)
