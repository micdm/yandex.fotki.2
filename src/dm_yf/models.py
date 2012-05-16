# encoding=utf8
'''
Модели данных.
@author: Mic, 2012
'''

from hashlib import md5

from dm_yf.log import logger
from dm_yf.protocol import Service
from dm_yf.utils import to_megabytes

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
        
    def _load_albums(self):
        '''
        Загружает список альбомов.
        '''
        logger.info('loading album list')
        albums = []
        for resource in self._resource.albums:
            album = Album(resource)
            albums.append(album)
        logger.info('album list loaded, %s albums found', len(albums))
        self._albums = albums
    
    @property
    def albums(self):
        '''
        Возвращает список альбомов.
        @return: string
        '''
        if self._albums is None:
            self._load_albums()
        return dict((album.title, album) for album in self._albums)
    
    def add(self, title):
        '''
        Добавляет новый альбом и возвращает его.
        @param title: string
        @return: Album
        '''
        logger.info('adding album "%s"', title)
        resource = self._resource.add(title)
        album = Album(resource)
        if self._albums is not None:
            self._albums.append(album)
        logger.info('album "%s" added', album)
        return album


class Album(object):
    '''
    Альбом.
    '''
    
    # Атрибуты, которые можно взять напрямую у ресурса:
    _ATTRIBUTES = ['title', 'published', 'updated']
    
    def __init__(self, resource):
        '''
        @param resource: Resource
        '''
        self._photos = None
        self._resource = resource
        
    def __str__(self):
        return '%s (%s)'%(self.title, self.photo_count)
    
    def __getattr__(self, name):
        if name in self._ATTRIBUTES:
            return getattr(self._resource, name)
        return super(Album, self).__getattr__(name)

    @property
    def photo_count(self):
        '''
        Возвращает количество фотографий в альбоме.
        @return: int
        '''
        if self._photos is None:
            return self._resource.photo_count
        return len(self._photos)
    
    def _load_photos(self):
        '''
        Загружает список фотографий.
        '''
        logger.info('loading photo list for album "%s"', self)
        photos = []
        for resource in self._resource.photos:
            photo = Photo(resource)
            photos.append(photo)
        logger.info('photo list loaded for album "%s", %s photos found', self, len(photos))
        self._photos = photos
    
    @property
    def photos(self):
        '''
        Возвращает список фотографий.
        @return: list
        '''
        if self._photos is None:
            self._load_photos()
        return dict((photo.title, photo) for photo in self._photos)
    
    def add(self, title, image_body):
        '''
        Добавляет фотографию в альбом и возвращает ее.
        @param title: string
        @param image_body: string
        @return: Photo
        '''
        logger.info('adding photo "%s"', title)
        resource = self._resource.add(title, image_body)
        photo = Photo(resource)
        if self._photos is not None:
            self._photos.append(photo)
        logger.info('photo "%s" added', photo)
        return photo


class Photo(object):
    '''
    Фотография.
    '''
    
    # Название фотографии по умолчанию, которое ставит сам сервис:
    DEFAULT_TITLE = 'Фотка'
    
    # Атрибуты, которые можно взять напрямую у ресурса:
    _ATTRIBUTES = ['title', 'published', 'updated', 'size']
    
    def __init__(self, resource):
        '''
        @param resource: Resource
        '''
        self._image = None
        self._resource = resource
        
    def __str__(self):
        return '%s (%sM)'%(self.title, to_megabytes(self.size))
    
    def __getattr__(self, name):
        if name in self._ATTRIBUTES:
            return getattr(self._resource, name)
        return super(Photo, self).__getattr__(name)

    def _load_image(self):
        '''
        Загружает тело фотографии.
        '''
        logger.info('loading photo "%s"', self)
        self._image = self._resource.content
        logger.info('photo "%s" loaded', self)
    
    @property
    def image(self):
        '''
        Возвращает тело фотографии.
        @return: string
        '''
        if self._image is None:
            self._load_image()
        return self._image
    
    def cleanup(self):
        '''
        Очищает кэшированное тело фотографии.
        Необходимо обязательно вызывать, если тело больше не нужно.
        '''
        logger.debug('cleanuping image for photo "%s"', self)
        self._image = None
        
