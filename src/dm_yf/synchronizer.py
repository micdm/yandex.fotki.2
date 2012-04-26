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
    
    def _get_path_to_photo(self, album, photo):
        '''
        Возвращает путь к фотографии.
        @param album: Album 
        @param photo: Photo
        @return: string
        '''
        filename = '%s.jpg'%md5(photo.get_id()).hexdigest()
        return os.path.join(self._path_to_album_list, album.get_title(), filename)
    
    def _get_file_count(self, path_to_album):
        '''
        Возвращает количество файлов в директории альбома.
        @param path_to_album: string
        @return: int
        '''
        _, _, filenames = os.walk(path_to_album).next()
        return len(filenames)
    
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
            logger.info('synchronizing photo %s/%s of album %s', i + 1, len(photos), album)
            self._sync_photo(album, photo)
        logger.debug('album %s synchronizing complete', album)

    def _store_image(self, path_to_photo, photo):
        '''
        Сохраняет фотографию в директории альбома.
        @param path_to_photo: string
        @param photo: Photo
        '''
        file_object = open(path_to_photo, 'w')
        file_object.write(photo.get_image())
        file_object.close()
        
    def _sync_photo(self, album, photo):
        '''
        Синхронизирует фотографию.
        @param album: Album
        @param photo: Photo
        '''
        logger.info('synchronizing photo %s of album %s', photo, album)
        path_to_photo = self._get_path_to_photo(album, photo)
        if os.path.exists(path_to_photo):
            if os.path.getsize(path_to_photo) == photo.get_size():
                logger.debug('photo %s already exists (%s), skipping', photo, path_to_photo)
                return
            logger.warning('photo %s already exists (%s) but has different size', photo, path_to_photo)
            return
        self._store_image(path_to_photo, photo)
        logger.debug('synchronizing photo %s of album %s complete', photo, album)
        
    def run(self):
        '''
        Запускает синхронизацию.
        '''
        logger.info('synchronizing remote to local on %s', self._path_to_album_list)
        album_list = AlbumList.get()
        for album in album_list.get_albums():
            self._sync_album(album)
        logger.debug('synchronizing remote to local complete on %s', self._path_to_album_list)


class LocalToRemoteSynchronizer(object):
    '''
    Удаленный синхронизатор.
    Выгружает локальные фотографии на сервер.
    '''
    
    def __init__(self, path_to_album_list):
        '''
        @param path_to_album_list: string
        '''
        self._path_to_album_list = path_to_album_list
        
    def _get_local_albums(self):
        '''
        Возвращает список локальных альбомов (название и путь).
        @return: list
        '''
        albums = []
        for dirname, _, _ in os.walk(self._path_to_album_list):
            title = dirname.replace(self._path_to_album_list, '')
            albums.append((title, dirname))
        return albums
    
    def _get_album_photos(self, path_to_album):
        '''
        Возвращает список фотографий в локальном альбоме (название и путь).
        @param path_to_album: string
        @return: list
        '''
        _, _, filenames = os.walk(path_to_album).next()
        photos = []
        for filename in filenames:
            _, extension = os.path.splitext(filename.lower())
            if extension in ('.jpg', '.jpeg'):
                path_to_photo = os.path.join(path_to_album, filename)
                photos.append((filename, path_to_photo))
        return photos
    
    def _sync_album(self, album_list, album_title, path_to_album):
        '''
        Синхронизирует альбом.
        @param album_list: AlbumList
        @param album_title: string
        @param path_to_album: string
        '''
        logger.info('synchronizing album "%s"', album_title)
        photos = self._get_album_photos(path_to_album)
        if not photos:
            logger.debug('album "%s" contains no photos, skipping', album_title)
            return
        logger.debug('album "%s" contains %s photos', album_title, len(photos))
        album = album_list.add_album(album_title)
        for i, (photo_title, path_to_photo) in zip(range(len(photos)), photos):
            logger.info('synchronizing photo %s/%s of album %s', i + 1, len(photos), album)
            self._sync_photo(album, photo_title, path_to_photo)
        logger.debug('album "%s" synchronizing complete', album_title)
        
    def _sync_photo(self, album, photo_title, path_to_photo):
        '''
        Синхронизирует фотографию.
        @param album: Album
        @param photo_title: string
        @param path_to_photo: string
        '''
        logger.info('synchronizing photo "%s" of album %s', photo_title, album)
        album.add_photo(photo_title, path_to_photo)
        logger.debug('synchronizing photo "%s" of album %s complete', photo_title, album)
    
    def run(self):
        '''
        Запускает синхронизацию.
        '''
        logger.info('synchronizing local to remote on %s', self._path_to_album_list)
        local_albums = self._get_local_albums()
        logger.debug('%s local albums found', len(local_albums))
        album_list = AlbumList.get()
        for title, path_to_album in local_albums:
            if title in album_list:
                # TODO: проверить, совпадает ли количество файлов
                logger.debug('remote album "%s" already exists, skipping', title)
            else:
                self._sync_album(album_list, title, path_to_album)
        logger.debug('synchronizing local to remote complete on %s', self._path_to_album_list)


class Synchronizer(object):
    '''
    Скомбинированный синхронизатор.
    '''
    
    def __init__(self, path_to_album_list):
        '''
        @param path_to_album_list: string
        '''
        path_to_album_list = self._fix_path_to_album_list(path_to_album_list)
        #self._local_synchronizer = RemoteToLocalSynchronizer(path_to_album_list)
        self._remote_synchronizer = LocalToRemoteSynchronizer(path_to_album_list)
        
    def _fix_path_to_album_list(self, path_to_album_list):
        '''
        Подправляет и путь к альбомам, если у него на конце нет слеша.
        @param path_to_album_list: string
        @return: string
        '''
        if not path_to_album_list.endswith(os.sep):
            logger.debug('no trailing slash found, adding one')
            path_to_album_list += os.sep
        return path_to_album_list

    def run(self):
        '''
        Запускает синхронизацию.
        '''
        #self._local_synchronizer.run()
        self._remote_synchronizer.run()
