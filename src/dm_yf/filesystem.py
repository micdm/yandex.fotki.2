# encoding=utf8
'''
Реализация виртуальной файловой системы средствами FUSE.
@author: Mic, 2012
'''

from datetime import datetime
import errno
import os.path
import stat
import tempfile

import fuse

from dm_yf.log import logger, set_log_file, set_logger_verbose
from dm_yf.models import AlbumList
from dm_yf.utils import to_timestamp


def _log_exception(func):
    '''
    Декоратор. Отслеживает исключения и выводит информацию о них.
    @param func: function
    @return: function
    '''
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.exception('exception occured')
            raise e
    return wrapper


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
    
    def __init__(self, *args, **kwargs):
        super(FotkiFilesystem, self).__init__(*args, **kwargs)
        self._buffers = {}

    def _getattr_for_root(self):
        '''
        Возвращает информацию для коревой директории.
        '''
        info = fuse.Stat()
        info.st_mode = stat.S_IFDIR | stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH
        album_list = AlbumList.get()
        # Для директорий высчитывается как 2 + количество поддиректорий:
        info.st_nlink = 2 + len(album_list.albums)
        context = self.GetContext()
        info.st_uid = context['uid']
        info.st_gid = context['gid']
        album_list = AlbumList.get()
        info.st_size = len(album_list.albums)
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
        # Для директорий высчитывается как 2 + количество поддиректорий:
        info.st_nlink = 2
        context = self.GetContext()
        info.st_uid = context['uid']
        info.st_gid = context['gid']
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
        # Для обычного файла равно 1:
        info.st_nlink = 1
        context = self.GetContext()
        info.st_uid = context['uid']
        info.st_gid = context['gid']
        info.st_size = photo.size
        info.st_atime = to_timestamp(datetime.utcnow())
        info.st_mtime = to_timestamp(photo.updated)
        info.st_ctime = to_timestamp(photo.published)
        return info
    
    def _getattr_for_buffer(self, path):
        '''
        Возвращает информацию для временного файла, в который пишется фотография.
        '''
        if path not in self._buffers:
            return None
        logger.debug('%s is buffer', path)
        info = fuse.Stat()
        file_stats = os.stat(self._buffers[path].name)
        info.st_mode = file_stats.st_mode
        info.st_nlink = file_stats.st_nlink
        info.st_uid = file_stats.st_uid
        info.st_gid = file_stats.st_gid
        info.st_size = file_stats.st_size
        info.st_atime = file_stats.st_atime
        info.st_mtime = file_stats.st_mtime
        info.st_ctime = file_stats.st_ctime
        return info

    @_log_exception
    def getattr(self, path): #@ReservedAssignment
        '''
        Возвращает информацию о файле.
        '''
        logger.debug('getting information about %s', path)
        path = _prepare_path(path)
        if not path:
            return self._getattr_for_root()
        info = self._getattr_for_buffer(path)
        if info:
            return info
        info = self._getattr_for_photo(path)
        if info:
            return info
        info = self._getattr_for_album(path)
        if info:
            return info
        logger.debug('no resource on %s found', path)
        return -errno.ENOENT
    
    @_log_exception
    def mkdir(self, path, mode):
        '''
        Создает директорию.
        '''
        logger.debug('creating directory %s', path)
        path = _prepare_path(path)
        album, photo = _parse_path(path)
        if album or photo:
            logger.warning('resource on %s already exists', path)
            return -errno.EEXIST
        album_list = AlbumList.get()
        album_list.add(path)
    
    @_log_exception
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
    
    @_log_exception
    def create(self, path, flags, mode):
        '''
        Создает пустой файл.
        '''
        logger.debug('creating %s with flags %s and mode %s', path, flags, mode)
        path = _prepare_path(path)
        album, photo = _parse_path(path)
        if album and photo:
            logger.warning('resource on %s already exists', path)
            return -errno.EEXIST
        if path in self._buffers:
            logger.warning('there is buffer for %s already', path)
            return -errno.EEXIST
        fileobj = tempfile.NamedTemporaryFile('w')
        self._buffers[path] = fileobj
        logger.debug('buffer created on %s for %s', fileobj.name, path)
    
    @_log_exception
    def open(self, path, flags): #@ReservedAssignment
        '''
        Вызывается перед попыткой открыть файл.
        '''
        logger.debug('opening %s with flags %s', path, flags)
        path = _prepare_path(path)
        access = os.O_RDONLY | os.O_WRONLY | os.O_RDWR
        if (flags & access) == os.O_RDONLY:
            _, photo = _parse_path(path)
            if photo is None:
                logger.warning('no photo found on %s', path)
                return -errno.ENOENT
        if (flags & access) == os.O_WRONLY:
            if path not in self._buffers:
                logger.warning('buffer for %s not opened yet', path)
                return -errno.EIO
        logger.warning('read or write only permitted on %s', path)
        return -errno.EACCES
        
    @_log_exception
    def read(self, path, size, offset):
        '''
        Возвращает порцию данных из файла.
        '''
        logger.debug('reading %s bytes with offset %s from %s', size, offset, path)
        path = _prepare_path(path)
        _, photo = _parse_path(path)
        if photo is None:
            logger.warning('no photo found on %s', path)
            return -errno.ENOENT
        image = photo.image
        chunk = image[offset:offset + size]
        if offset + size >= len(image):
            photo.cleanup()
        return chunk
    
    @_log_exception
    def write(self, path, buf, offset):
        '''
        Записывает в файл порцию данных.
        '''
        logger.debug('writing %s bytes with offset %s to %s', len(buf), offset, path)
        path = _prepare_path(path)
        if path not in self._buffers:
            logger.warning('buffer for %s not opened yet', path)
            return -errno.EIO
        fileobj = self._buffers[path]
        fileobj.seek(offset)
        fileobj.write(buf)
    
    @_log_exception
    def flush(self, path):
        '''
        Заставляет файл сохранить изменения.
        '''
        logger.debug('flushing %s', path)
        path = _prepare_path(path)
        if path not in self._buffers:
            logger.warning('buffer for %s not opened yet', path)
            return -errno.EIO
        self._buffers[path].flush()
    
    @_log_exception
    def release(self, path, fh):
        '''
        Закрывает файл.
        '''
        logger.debug('closing %s', path)
        path = _prepare_path(path)
        if path not in self._buffers:
            logger.warning('buffer for %s not opened yet', path)
            return
        self._buffers[path].close()
        del self._buffers[path]


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
