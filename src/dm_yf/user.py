# encoding=utf8
'''
Представление пользователя.
@author: Mic, 2012
'''

from dm_yf.atompub import Service

# Адрес сервисного документа:
SERVICE_URL = 'http://api-fotki.yandex.ru/api/me/'

class User(object):
    '''
    Класс для представления пользователя.
    '''

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
