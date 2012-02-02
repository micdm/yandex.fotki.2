# encoding=utf8
'''
Классы для сохранения данных.
@author: Mic, 2012
'''

from xml.etree.ElementTree import Element, TreeBuilder

from dm_yf.atompub import ATOM_NS
from dm_yf.converters import AlbumConverter
from dm_yf.fotki import Album
from dm_yf.log import logger
from dm_yf.user import User

class AlbumListStorer(object):
    '''
    Сохранение списка альбомов.
    '''
    
    def __init__(self):
        self._album_list = None
        
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
        collection = User.get_album_collection()
        entry = collection.add_entry(node)
        new_album = AlbumConverter.from_entry(entry)
        album.set_id(new_album.get_id())
        album.set_state(Album.STATE_SYNCED)
        
    def _get_album_entry(self, collection, album):
        '''
        Находит элемент, соответствующий альбому.
        @param collection: Collection
        @param album: Album
        @return: Entry
        '''
        for entry in collection.get_entries():
            if album.get_id() == entry.get_id():
                return entry
        return None
    
    def _delete_album(self, album):
        '''
        Удаляет альбом.
        @param album: Album
        '''
        logger.debug('deleting album %s', album)
        collection = User.get_album_collection()
        entry = self._get_album_entry(collection, album)
        collection.delete_entry(entry)
    
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
    
    def store(self, album_list):
        '''
        Сохраняет список альбомов.
        @param album_list: AlbumList
        '''
        logger.info('storing album list')
        self._album_list = album_list
        albums = album_list.get_albums()
        for album in albums:
            self._store_album(album)
        album_list.clean()
        logger.info('album list stored')
