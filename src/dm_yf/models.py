# encoding=utf8
'''
Модели данных.
@author: Mic, 2012
'''

from dm_yf.protocol import Service

# Адрес сервисного документа:
SERVICE_URL = 'http://api-fotki.yandex.ru/api/me/'

class AlbumList(object):
    '''
    Список альбомов.
    '''
    
    _album_list = None
    
    @classmethod
    def _get(cls):
        '''
        Создает новый объект списка альбомов.
        @return: AlbumList
        '''
        service = Service.get(SERVICE_URL)
        resource = service.get_resource('album-list')
        if resource is None:
            return None
        return cls(resource)
    
    @classmethod
    def get(cls):
        '''
        Синглтон.
        @return: AlbumList
        '''
        if cls._album_list is None:
            cls._album_list = cls._get()
        return cls._album_list
    
    def __init__(self, resource):
        '''
        @param resource: Resource
        '''
        self._albums = None
        self._resource = resource
        
    def _get_albums(self):
        '''
        Загружает список альбомов.
        @return: list
        '''
        albums = []
        resources = self._resource.get_resources('self')
        for resource in resources:
            album = Album(resource)
            albums.append(album)
        return albums
        
    def get_albums(self):
        '''
        Возвращает список альбомов.
        @return: string
        '''
        if self._albums is None:
            self._albums = self._get_albums()
        return self._albums
    
    def add_album(self, title):
        '''
        Добавляет новый альбом.
        @param title: string
        '''
        self._resource.add_album(title)
        self._albums = None


class Album(object):
    '''
    Альбом.
    '''
    
    def __init__(self, resource):
        '''
        @param resource: Resource
        '''
        self._photos = None
        self._resource = resource
        
    def __str__(self):
        return '<Album "%s" (%s)>'%(self.get_title(), self.get_image_count())
        
    def get_title(self):
        '''
        Возвращает название альбома.
        @return: string
        '''
        return self._resource.get_title()
    
    def get_image_count(self):
        '''
        Возвращает количество фотографий в альбоме.
        @return: int
        '''
        return self._resource.get_image_count()
    
    def _get_photos(self):
        '''
        Загружает список фотографий.
        @return: list
        '''
        photos = []
        resources = self._resource.get_resources('photos')
        for resource in resources:
            photo = Photo(resource)
            photos.append(photo)
        return photos
    
    def get_photos(self):
        '''
        Возвращает список фотографий.
        @return: list
        '''
        if self._photos is None:
            self._photos = self._get_photos()
        return self._photos


class Photo(object):
    '''
    Фотография.
    '''
    
    def __init__(self, resource):
        '''
        @param resource: Resource
        '''
        self._resource = resource
        
    def __str__(self):
        return '<Photo "%s" (%sM)>'%(self.get_title().encode('utf8'), self.get_size(True))
        
    def get_title(self):
        '''
        Возвращает название фотографии.
        @return: string
        '''
        return self._resource.get_title()
    
    def get_size(self, as_megabytes=False):
        '''
        Возвращает размер фотографии в байтах.
        @return: int
        '''
        size = self._resource.get_size()
        if as_megabytes:
            return round(float(size) / 2**20, 2)
        return size
        
    def get_image(self):
        '''
        Возвращает тело фотографии.
        @return: string
        '''
        return self._resource.get_content()
