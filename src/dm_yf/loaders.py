# encoding=utf8
'''
Загрузчики данных.
@author: Mic, 2012
'''

from dm_yf.atompub import Service, ATOM_NS
from dm_yf.fotki import Album

# Адрес сервисного документа:
SERVICE_URL = 'http://api-fotki.yandex.ru/api/me/'

# Пространство имен:
FOTKI_NS = 'yandex:fotki'

class AlbumListLoader(object):
    '''
    Загрузчик списка альбомов.
    '''
    
    def _get_all_collections(self):
        '''
        Возвращает все коллекции.
        @return: list
        '''
        service = Service(SERVICE_URL)
        return service.get_collections()

    def _get_album_collection(self):
        '''
        Выбирает из коллекций коллекцию с альбомами.
        @return: Collection
        '''
        for collection in self._get_all_collections():
            node = collection.get_node()
            if node.attrib['id'] == 'album-list':
                return collection
        return None
    
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
    
    def load(self):
        '''
        Загружает список альбомов.
        @return: AlbumList
        '''
        collection = self._get_album_collection()
        return map(self._get_album_from_entry, collection.get_entries())
