# encoding=utf8
'''
Классы для сущностей Яндекс.Фотки.
@author: Mic, 2012
'''

# Пространство имен:
FOTKI_NS = 'yandex:fotki'

class AlbumList(object):
    '''
    Список альбомов.
    '''

    def __init__(self, albums):
        '''
        @param albums: list
        '''
        self._albums = albums
        
    def get_albums(self):
        '''
        Возвращает список альбомов.
        @return: list
        '''
        return self._albums

    def add(self, album):
        '''
        Добавляет новый альбом.
        @param album: Album
        '''
        self._albums.append(album)
        album.set_state(Album.STATE_NEW)
        
    def delete(self, album):
        '''
        Удаляет альбом.
        @param album: Album
        '''
        index = self._albums.index(album)
        self._albums[index].set_state(Album.STATE_DELETED)
        
    def clean(self):
        '''
        Очищает список, убирая альбомы, помеченные удаленными.
        '''
        self._albums = [album for album in self._albums if album.get_state() != Album.STATE_DELETED]


class Album(object):
    '''
    Альбом.
    '''
    
    STATE_NEW = 'new'
    STATE_SYNCED = 'synced'
    STATE_DELETED = 'deleted'
    
    def __init__(self, id, title, photo_count=0, state=STATE_SYNCED):
        '''
        @param id: string
        @param title: string
        @param photo_count: int
        @param state: string
        '''
        self._id = id
        self._title = title
        self._photo_count = photo_count
        self._state = state
        
    def __str__(self):
        return '"%s"'%self._title
        
    def __eq__(self, other):
        '''
        Будем считать альбомы одинаковыми, если у них совпадают идентификаторы.
        @param other: Album
        '''
        return self._id == other.get_id()
        
    @classmethod
    def create(cls, title):
        '''
        Возвращает новый альбом.
        @param title: string
        @return: Album
        '''
        return cls(None, title, state=cls.STATE_NEW)
    
    def get_id(self):
        '''
        Возвращает идентификатор альбома.
        @return: string
        '''
        return self._id
    
    def set_id(self, id):
        '''
        Задает идентификатор альбома.
        @param id: string
        '''
        self._id = id
    
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
