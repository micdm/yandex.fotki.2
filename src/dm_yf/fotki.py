# encoding=utf8
'''
Классы для сущностей Яндекс.Фотки.
@author: Mic, 2012
'''

from xml.etree.ElementTree import tostring

from dm_yf.atompub import ATOM_NS, Service, Entry

# Пространство имен:
FOTKI_NS = 'yandex:fotki'

class User(object):
    '''
    Пользователь.
    У пользователя есть несколько больших коллекций.
    '''
    
    # Адрес сервисного документа:
    SERVICE_URL = 'http://api-fotki.yandex.ru/api/me/'
    
    def __init__(self):
        self._album_collection = None
    
    def _get_all_collections(self):
        '''
        Возвращает все коллекции.
        @return: list
        '''
        service = Service(self.SERVICE_URL)
        return service.get_collections()
    
    def _get_album_collection(self):
        '''
        Выбирает из коллекций коллекцию с альбомами.
        @return: Collection
        '''
        if self._album_collection is not None:
            return self._album_collection
        for collection in self._get_all_collections():
            node = collection.get_node()
            if node.attrib['id'] == 'album-list':
                self._album_collection = collection
                break
        return self._album_collection
    
    def _get_album_from_entry(self, entry):
        '''
        Получает альбом из элемента.
        @param entry: Entry
        @return: Album
        '''
        node = entry.get_node()
        title = node.find('{%s}title'%ATOM_NS).text.encode('utf8')
        photo_count = int(node.find('{%s}image-count'%FOTKI_NS).attrib['value'])
        return Album(entry, title, photo_count)
    
    def get_albums(self):
        '''
        Возвращает список альбомов.
        @return: list
        '''
        collection = self._get_album_collection()
        return map(self._get_album_from_entry, collection.get_entries())
    
#    def _get_entry_from_album(self, album):
#        node = 
#        return Entry(None, node)
    
    def add_album(self, title, summary=None):
        '''
        Добавляет новый альбом.
        @param title: string
        '''
        collection = self._get_album_collection()
        
    
    def remove_album(self):
        '''
        Удаляет альбом.
        '''
        raise NotImplementedError()


class Album(object):
    '''
    Альбом.
    Внутри альбома хранятся фотографии.
    '''
    
    def __init__(self, entry, title, photo_count):
        '''
        @param entry: Entry
        @param title: string
        @param photo_count: int
        '''
        self._entry = entry
        self._title = title
        self._photo_count = photo_count
    
    def get_photos(self):
        '''
        Возвращает список фотографий.
        @return: list
        '''
        raise NotImplementedError()


class Photo(object):
    '''
    Фотография.
    '''
