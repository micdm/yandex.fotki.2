# encoding=utf8
'''
Синхронизация локальной директории и аккаунта Фоток.
@author: Mic, 2012
'''

from hashlib import md5
import os

from dm_yf.log import getLogger
from dm_yf.models import AlbumList

logger = getLogger()

class RemoteToLocalSynchronizer(object):
    '''
    Локальный синхронизатор.
    Создает копию удаленных данных в локальном хранилище.
    '''
    
    def __init__(self, path_to_album_list):
        '''
        @param path_to_album_list: string
        '''
        self._path_to_album_list = path_to_album_list
    
    def _get_path_to_album(self, album):
        '''
        Возвращает путь к директории альбома.
        Создает директорию, если ее еще нет.
        @param album: Album
        @return: string
        '''
        path_to_album = os.path.join(self._path_to_album_list, album.get_title())
        if not os.path.exists(path_to_album):
            logger.debug('album directory %s not exists, creating', path_to_album)
            os.makedirs(path_to_album)
        return path_to_album
    
    def _get_image_name(self, image_body):
        '''
        Возвращает имя файла-картинки.
        @param image_body: string
        @return: string
        '''
        return '%s.jpg'%md5(image_body).hexdigest()
    
    def _get_path_to_photo(self, album, image_name):
        '''
        Возвращает путь к фотографии.
        @param album: Album 
        @param image_name: string
        @return: string
        '''
        return os.path.join(self._path_to_album_list, album.get_title(), image_name)
    
    def _get_file_count(self, path_to_album):
        '''
        Возвращает количество файлов в директории альбома.
        @param path_to_album: string
        @return: int
        '''
        return len(os.listdir(path_to_album))
    
    def _store_image(self, path_to_photo, image_body):
        '''
        Сохраняет фотографию в директории альбома.
        @param path_to_photo: string
        @param image_body: string
        '''
        file_object = open(path_to_photo, 'w')
        file_object.write(image_body)
        file_object.close()
        
    def _sync_photo(self, album, photo):
        '''
        Синхронизирует фотографию.
        @param album: Album
        @param photo: Photo
        '''
        image_body = photo.get_image()
        image_name = self._get_image_name(image_body)
        logger.info('synchronizing photo %s of album %s, filename is %s', photo, album, image_name)
        path_to_photo = self._get_path_to_photo(album, image_name)
        if os.path.exists(path_to_photo):
            if os.path.getsize(path_to_photo) == photo.get_size():
                logger.debug('photo %s already exists, skipping', photo)
                return
            logger.warning('photo %s already exists but has different size', photo)
            return
        self._store_image(path_to_photo, image_body)
        logger.debug('synchronizing photo %s of album %s complete', photo, album)
    
    def _sync_album(self, album):
        '''
        Синхронизирует альбом: создает директорию и загружает фотографии.
        @param album: Album
        '''
        logger.info('synchronizing album %s', album)
        path_to_album = self._get_path_to_album(album)
        file_count = self._get_file_count(path_to_album)
        if file_count == album.get_image_count():
            logger.debug('looks like album is already synchronized, skipping')
            return
        photos = album.get_photos()
        for i, photo in zip(range(len(photos)), photos):
            logger.info('synchronizing photo %s/%s of album %s', i, len(photos), album)
            self._sync_photo(album, photo)
        logger.debug('album %s synchronizing complete', album)
        
    def run(self):
        '''
        Запускает синхронизацию.
        '''
        logger.info('synchronizing local albums on %s', self._path_to_album_list)
        album_list = AlbumList.get()
        for album in album_list.get_albums():
            self._sync_album(album)
        logger.debug('local albums synchronizing complete on %s', self._path_to_album_list)


class Synchronizer(object):
    '''
    Скомбинированный синхронизатор.
    '''
    
    def __init__(self, path_to_album_list):
        '''
        @param path_to_album_list: string
        '''
        self._local_synchronizer = RemoteToLocalSynchronizer(path_to_album_list)
        
    def run(self):
        '''
        Запускает синхронизацию.
        '''
        self._local_synchronizer.run()
