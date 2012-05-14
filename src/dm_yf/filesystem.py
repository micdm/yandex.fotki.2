# encoding=utf8
'''
Реализация виртуальной файловой системы средствами FUSE.
@author: Mic, 2012
'''

from datetime import datetime
import errno
import os.path
import stat

import fuse

from dm_yf.log import logger, set_log_file, set_logger_verbose
from dm_yf.models import AlbumList
from dm_yf.utils import to_timestamp

def _prepare_path(path):
    '''
    Подправляет путь: удаляет ведущий слеш.
    @param path: string
    @return: string
    '''
    return path.replace(os.path.sep, '', 1)


def _parse_path(path):
    '''
    Разбирает путь и возвращает альбом и фотографию, которые находятся по этому пути.
    @param path: string
    @return: Album, Photo
    '''
    album_list = AlbumList.get()
    album = album_list.albums.get(path)
    if album:
        return album, None
    album_title, photo_title = os.path.split(path)
    album = album_list.albums.get(album_title)
    if album is None:
        return None, None
    photo = album.photos.get(photo_title)
    return album, photo


class FotkiFilesystem(fuse.Fuse):
    '''
    Реализация виртуальной файловой системы средствами FUSE.
    '''

    def _getattr_for_root(self):
        '''
        Возвращает информацию для коревой директории.
        '''
        info = fuse.Stat()
        info.st_mode = stat.S_IFDIR | stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH
        info.st_nlink = 3
        return info
    
    def _getattr_for_album(self, path):
        '''
        Возвращает информацию для альбома.
        '''
        album, _ = _parse_path(path)
        if album is None:
            return None
        logger.debug('%s is album', path)
        info = fuse.Stat()
        info.st_mode = stat.S_IFDIR | stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH
        info.st_nlink = 3
        info.st_uid = os.getuid()
        info.st_gid = os.getgid()
        info.st_size = album.photo_count
        info.st_atime = to_timestamp(datetime.utcnow())
        info.st_mtime = to_timestamp(album.updated)
        info.st_ctime = to_timestamp(album.published) 
        return info
    
    def _getattr_for_photo(self, path):
        '''
        Возвращает информацию для фотографии.
        '''
        _, photo = _parse_path(path)
        if photo is None:
            return None
        logger.debug('%s is photo', path)
        info = fuse.Stat()
        info.st_mode = stat.S_IFREG | stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH
        info.st_nlink = 1
        info.st_uid = os.getuid()
        info.st_gid = os.getgid()
        info.st_size = photo.size
        info.st_atime = to_timestamp(datetime.utcnow())
        info.st_mtime = to_timestamp(photo.updated)
        info.st_ctime = to_timestamp(photo.published)
        return info

    def getattr(self, path): #@ReservedAssignment
        '''
        Возвращает информацию о файле.
        '''
        logger.debug('getting information about %s', path)
        path = _prepare_path(path)
        if not path:
            return self._getattr_for_root()
        info = self._getattr_for_photo(path)
        if info:
            return info
        info = self._getattr_for_album(path)
        if info:
            return info
        return -errno.ENOENT

    def readdir(self, path, offset):
        '''
        Возвращает содержимое директории.
        '''
        # TODO: давать ссылки на вложенные альбомы
        logger.debug('reading directory %s', path)
        yield fuse.Direntry('.')
        yield fuse.Direntry('..')
        album_list = AlbumList.get()
        path = _prepare_path(path)
        if not path:
            for album in album_list.albums.values():
                yield fuse.Direntry(album.title)
        else:
            album = album_list.albums[path]
            for photo in album.photos.values():
                yield fuse.Direntry(photo.title)
                
    def mkdir(self, path, mode):
        '''
        Создает директорию.
        '''
        logger.debug('creating directory %s', path)
        path = _prepare_path(path)
        album, photo = _parse_path(path)
        if album or photo:
            return -errno.EEXIST
        album_list = AlbumList.get()
        album_list.add(path)
                
    def open(self, path, flags): #@ReservedAssignment
        '''
        Вызывается перед попыткой открыть файл.
        '''
        logger.debug('opening %s with flags %s', path, flags)
        access = os.O_RDONLY | os.O_WRONLY | os.O_RDWR
        if (flags & access) != os.O_RDONLY:
            return -errno.EACCES
        path = _prepare_path(path)
        _, photo = _parse_path(path)
        if photo is None:
            return -errno.ENOENT
    
    def read(self, path, size, offset):
        '''
        Возвращает порцию данных из файла.
        '''
        logger.debug('reading %s bytes with offset %s from %s', size, offset, path)
        path = _prepare_path(path)
        _, photo = _parse_path(path)
        if photo is None:
            return -errno.ENOENT
        image = photo.image
        chunk = image[offset:offset + size]
        if offset + size >= len(image):
            photo.cleanup()
        return chunk


def start():
    '''
    Монтирует директорию и запускает всю FUSE-кухню.
    '''
    set_log_file('filesystem.log')
    set_logger_verbose()
    fuse.fuse_python_api = (0, 2)
    fs = FotkiFilesystem()
    fs.parse()
    fs.main()
