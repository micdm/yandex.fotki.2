# encoding=utf8
'''
Представление пользователя.
@author: Mic, 2012
'''

from dm_yf.atompub import Service
from dm_yf.fotki import AlbumList

# Адрес сервисного документа:
SERVICE_URL = 'http://api-fotki.yandex.ru/api/me/'

class User(object):
    '''
    Класс для представления пользователя.
    '''

    # Список альбомов:
    _album_list = None

    @classmethod
    def _get_all_collections(self):
        '''
        Возвращает все коллекции.
        @return: list
        '''
        service = Service(SERVICE_URL)
        return service.get_collections()

    @classmethod
    def get_album_collection(cls):
        '''
        Выбирает из коллекций коллекцию с альбомами.
        @return: Collection
        '''
        for collection in cls._get_all_collections():
            node = collection.get_node()
            if node.attrib['id'] == 'album-list':
                return collection
        return None
    
    @classmethod
    def get_album_list(cls):
        '''
        Возвращает список альбомов.
        @return: AlbumList
        '''
        if cls._album_list is None:
            cls._album_list = AlbumList()
        return cls._album_list
