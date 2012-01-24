# encoding=utf8
'''
Классы для сущностей Яндекс.Фотки.
@author: Mic, 2012
'''

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
        
    def delete(self):
        '''
        Удаляет альбом.
        '''
        raise NotImplementedError()


class Album(object):
    '''
    Альбом.
    '''
    
    def __init__(self, title, photo_count=0):
        '''
        @param title: string
        @param photo_count: int
        '''
        self._title = title
        self._photo_count = photo_count
        
    def __eq__(self, other):
        '''
        Будем считать альбомы одинаковыми, если у них совпадает название.
        @param other: Album
        '''
        return self._title == other.get_title()
    
    def get_title(self):
        '''
        Возвращает название альбома.
        @return: string
        '''
        return self._title
    
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
