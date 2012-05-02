# encoding=utf8
'''
Модели данных.
@author: Mic, 2012
'''

from hashlib import md5

from dm_yf.log import logger
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
        
    def __contains__(self, title):
        '''
        @param title: string
        '''
        return self.get_album(title) is not None
        
    def _load_albums(self):
        '''
        Загружает список альбомов.
        '''
        logger.info('loading album list')
        albums = []
        for resource in self._resource.get_albums():
            album = Album(resource)
            albums.append(album)
        logger.info('album list loaded, %s albums found', len(albums))
        self._albums = albums
        
    def get_albums(self):
        '''
        Возвращает список альбомов.
        @return: string
        '''
        if self._albums is None:
            self._load_albums()
        return self._albums
    
    def get_album(self, title):
        '''
        Возвращает альбом по названию.
        @param title: string
        @return: Album
        '''
        for album in self.get_albums():
            if album.get_title() == title:
                return album
        return None
    
    def add_album(self, title):
        '''
        Добавляет новый альбом и возвращает его.
        @param title: string
        @return: Album
        '''
        logger.info('adding album "%s"', title)
        resource = self._resource.add_album(title)
        album = Album(resource)
        if self._albums is None:
            self._load_albums()
        self._albums.append(album)
        logger.info('album "%s" added', album)
        return album


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
        return '%s (%s)'%(self.get_title(), self.get_photo_count())
    
    def __contains__(self, title):
        '''
        @param title: string
        '''
        return self.get_photo(title) is not None
        
    def get_title(self):
        '''
        Возвращает название альбома.
        @return: string
        '''
        return self._resource.get_title()
    
    def get_photo_count(self):
        '''
        Возвращает количество фотографий в альбоме.
        @return: int
        '''
        if self._photos is None:
            return self._resource.get_photo_count()
        return len(self._photos)
    
    def _load_photos(self):
        '''
        Загружает список фотографий.
        '''
        logger.info('loading photo list for album "%s"', self)
        photos = []
        for resource in self._resource.get_photos():
            photo = Photo(resource)
            photos.append(photo)
        logger.info('photo list loaded for album "%s", %s photos found', self, len(photos))
        self._photos = photos
    
    def get_photos(self):
        '''
        Возвращает список фотографий.
        @return: list
        '''
        if self._photos is None:
            self._load_photos()
        return self._photos
    
    def get_photo(self, title):
        '''
        Возвращает фотографию по названию.
        @param title: string
        @return: Photo
        '''
        for photo in self.get_photos():
            if photo.get_title() == title:
                return photo
        return None
    
    def add_photo(self, title, path_to_image):
        '''
        Добавляет фотографию в альбом и возвращает ее.
        @param title: string
        @param path_to_image: string
        @return: Photo
        '''
        logger.info('adding photo "%s" at %s', title, path_to_image)
        image_body = open(path_to_image).read()
        resource = self._resource.add_photo(title, image_body)
        photo = Photo(resource)
        if self._photos is None:
            self._load_photos()
        self._photos.append(photo)
        logger.info('photo "%s" added', photo)
        return photo


class Photo(object):
    '''
    Фотография.
    '''
    
    # Название фотографии по умолчанию, которое ставит сам сервис:
    DEFAULT_TITLE = 'Фотка'
    
    def __init__(self, resource):
        '''
        @param resource: Resource
        '''
        self._resource = resource
        
    def __str__(self):
        return '%s (%sM)'%(self.get_title(), self.get_size(True))
    
    def get_id(self):
        '''
        Возвращает идентификатор фотографии.
        @return: string
        '''
        return self._resource.get_id()
        
    def get_title(self):
        '''
        Возвращает название фотографии.
        Если название не задано, генерирует название из идентификатора фотографии.
        @return: string
        '''
        title = self._resource.get_title()
        logger.warning('TITLE IS %s, TYPE IS %s', title, type(title))
        if title == self.DEFAULT_TITLE:
            return '%s.jpg'%md5(self.get_id()).hexdigest()
        return title
    
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
        logger.info('loading photo "%s"', self)
        content = self._resource.get_content()
        logger.info('photo "%s" loaded', self)
        return content
