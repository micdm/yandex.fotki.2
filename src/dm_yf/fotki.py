# encoding=utf8
'''
Классы для сущностей Яндекс.Фотки.
@author: Mic, 2012
'''

class AlbumList(object):
    '''
    Список альбомов.
    '''

    def __init__(self):
        '''
        @param albums: list
        '''
        self._albums = None
        
    def get(self):
        '''
        Возвращает список альбомов.
        @return: list
        '''
        from dm_yf.loaders import AlbumListLoader
        if self._albums is None:
            self._albums = AlbumListLoader().load()
        return self._albums


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
