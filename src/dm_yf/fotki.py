# encoding=utf8
'''
Классы для сущностей Яндекс.Фотки.
@author: Mic, 2012
'''

class AlbumList(object):
    '''
    Список альбомов.
    '''

    def __init__(self, albums, collection):
        '''
        @param albums: list
        @param collection: Collection
        '''
        self._albums = albums
        self._collection = collection
        
    def get_albums(self):
        '''
        Возвращает список альбомов.
        @return: list
        '''
        return self._albums
    
    def get_collection(self):
        '''
        Возвращает коллекцию альбомов.
        @return: Collection
        '''
        return self._collection
    
    def add(self, album):
        '''
        Добавляет новый альбом.
        @param album: Album
        '''
        self._albums.append(album)
        
    def delete(self):
        '''
        Удаляет альбом.
        '''
        raise NotImplementedError()


class Album(object):
    '''
    Альбом.
    '''
    
    STATE_NEW = 'new'
    STATE_SYNCED = 'synced'
    STATE_DELETED = 'deleted'
    
    def __init__(self, title, photo_count=0, state=STATE_SYNCED):
        '''
        @param title: string
        @param photo_count: int
        @param state: string
        '''
        self._title = title
        self._photo_count = photo_count
        self._state = state
        
    def __str__(self):
        return '"%s"'%self._title
        
    def __eq__(self, other):
        '''
        Будем считать альбомы одинаковыми, если у них совпадает название.
        @param other: Album
        '''
        return self._title == other.get_title()
        
    @classmethod
    def create(cls, title):
        '''
        Возвращает новый альбом.
        @param title: string
        @return: Album
        '''
        return cls(title, state=cls.STATE_NEW)
    
    def get_title(self):
        '''
        Возвращает название альбома.
        @return: string
        '''
        return self._title
    
    def get_state(self):
        '''
        Возвращает состояние альбома.
        @return: string
        '''
        return self._state
    
    def set_state(self, state):
        '''
        Устанавливает состояние альбома.
        @param state: string
        '''
        self._state = state
    
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
