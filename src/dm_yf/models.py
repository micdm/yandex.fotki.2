# encoding=utf8

from dm_yf.protocol import Service

# Адрес сервисного документа:
SERVICE_URL = 'http://api-fotki.yandex.ru/api/me/'

class AlbumList(object):
    
    @classmethod
    def get(cls):
        service = Service.get(SERVICE_URL)
        resource = service.get_resource('album-list')
        if resource is None:
            return None
        return cls(resource)
    
    def __init__(self, resource):
        self._albums = None
        self._resource = resource
        
    def _get_albums(self):
        albums = []
        resources = self._resource.get_resources('self')
        for resource in resources:
            album = Album(resource)
            albums.append(album)
        return albums
        
    def get_albums(self):
        if self._albums is None:
            self._albums = self._get_albums()
        return self._albums


class Album(object):
    
    def __init__(self, resource):
        self._photos = None
        self._resource = resource
    
    def _get_photos(self):
        photos = []
        resources = self._resource.get_resources('photos')
        for resource in resources:
            photo = Photo(resource)
            photos.append(photo)
        return photos
    
    def get_photos(self):
        if self._photos is None:
            self._photos = self._get_photos()
        return self._photos


class Photo(object):
    
    def __init__(self, resource):
        self._resource = resource
        
    def get_image(self):
        return self._resource.get_media()
