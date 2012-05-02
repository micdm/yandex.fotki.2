# encoding=utf8
'''
Реализация виртуальной файловой системы средствами FUSE.
@author: Mic, 2012
'''

import os.path
import stat

import fuse

from dm_yf.log import logger, set_log_file, set_logger_verbose
from dm_yf.models import AlbumList
import errno

def _prepare_path(path):
    '''
    Подправляет путь: удаляет ведущий слеш.
    @param path: string
    @return: string
    '''
    return path.replace(os.path.sep, '', 1)


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
        album_list = AlbumList.get()
        album = album_list.get_album(path)
        if not album:
            return None
        logger.debug('%s is album', path)
        info = fuse.Stat()
        info.st_mode = stat.S_IFDIR | stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH
        info.st_nlink = 3
        return info
    
    def _getattr_for_photo(self, path):
        '''
        Возвращает информацию для фотографии.
        '''
        album_title, photo_title = os.path.split(path)
        album_list = AlbumList.get()
        album = album_list.get_album(album_title)
        if not album:
            return None
        photo = album.get_photo(photo_title)
        if not photo:
            return None
        logger.debug('%s is photo', path)
        info = fuse.Stat()
        info.st_mode = stat.S_IFREG | stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH
        info.st_nlink = 1
        info.st_size = photo.get_size()
        return info

    def getattr(self, path):
        '''
        Возвращает информацию о файле.
        '''
        # TODO: проставить метки времени
        logger.debug('getting information about %s', path)
        path = _prepare_path(path)
        if not path:
            return self._getattr_for_root()
        info = self._getattr_for_album(path)
        if info:
            return info
        info = self._getattr_for_photo(path)
        if info:
            return info
        return -errno.ENOENT

    def readdir(self, path, offset):
        '''
        Возвращает содержимое директории.
        '''
        logger.debug('reading directory %s', path)
        yield fuse.Direntry('.')
        yield fuse.Direntry('..')
        album_list = AlbumList.get()
        path = _prepare_path(path)
        if not path:
            for album in album_list.get_albums():
                yield fuse.Direntry(album.get_title())
        else:
            album = album_list.get_album(path)
            for photo in album.get_photos():
                yield fuse.Direntry(photo.get_title())


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
