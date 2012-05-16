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


class PathInfo(object):
    '''
    Информация о пути.
    '''
    
    def __init__(self, album=None, photo=None, buffer=None): #@ReservedAssignment
        '''
        @param album: Album
        @param photo: Photo
        @param buffer: file
        '''
        self.album = album
        self.photo = photo
        self.buffer = buffer


class FotkiFilesystem(fuse.Fuse):
    '''
    Реализация виртуальной файловой системы средствами FUSE.
    '''
    
    def __init__(self, *args, **kwargs):
        super(FotkiFilesystem, self).__init__(*args, **kwargs)
        self.multithreaded = False
        self._buffers = {}
        
    def _is_removing_allowed(self):
        '''
        Возвращает, разрешено ли удаление альбомов и фотографий.
        @return: bool
        '''
        return bool(self.cmdline[0].is_removing_allowed)
        
    def _prepare_path(self, path):
        '''
        Подправляет путь: удаляет ведущий слеш.
        @param path: string
        @return: string
        '''
        return path.replace(os.path.sep, '', 1)
    
    def _split_path(self, path):
        '''
        Разбиавет путь и возвращает название альбома + название фотографии.
        @param path: string
        @return: string, string
        '''
        return os.path.split(path)
        
    def _parse_path(self, path):
        '''
        Разбирает путь и возвращает информацию относительно альбома и фотографии,
        которые могут находиться по этому пути.
        @param path: string
        @return: PathInfo
        '''
        album_list = AlbumList.get()
        if os.path.splitext(path)[1] == '.jpg':
            if path in self._buffers:
                return PathInfo(buffer=self._buffers[path])
            album_title, photo_title = self._split_path(path)
            album = album_list.albums.get(album_title)
            if album is None:
                return PathInfo()
            photo = album.photos.get(photo_title)
            if photo:
                return PathInfo(photo=photo)
            return PathInfo()
        album = album_list.albums.get(path)
        if album:
            return PathInfo(album=album)
        return PathInfo()
    
    def _get_access_mode(self, is_directory):
        '''
        Возвращает режим доступа.
        @param is_directory: bool
        @return: bool
        '''
        default = stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH
        if self._is_removing_allowed() and is_directory:
            return default | stat.S_IWUSR | stat.S_IXUSR
        return default

    def _getattr_for_root(self):
        '''
        Возвращает информацию для коревой директории.
        @return: Stat
        '''
        info = fuse.Stat()
        info.st_mode = stat.S_IFDIR | self._get_access_mode(True)
        album_list = AlbumList.get()
        # Для директорий высчитывается как 2 + количество поддиректорий:
        info.st_nlink = 2 + len(album_list.albums)
        context = self.GetContext()
        info.st_uid = context['uid']
        info.st_gid = context['gid']
        album_list = AlbumList.get()
        info.st_size = len(album_list.albums)
        return info
    
    def _getattr_for_album(self, album):
        '''
        Возвращает информацию для альбома.
        @param album: Album
        @return: Stat
        '''
        info = fuse.Stat()
        info.st_mode = stat.S_IFDIR | self._get_access_mode(True)
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
    
    def _getattr_for_photo(self, photo):
        '''
        Возвращает информацию для фотографии.
        @param photo: Photo
        @return: Stat
        '''
        info = fuse.Stat()
        info.st_mode = stat.S_IFREG | self._get_access_mode(False)
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
    
    def _getattr_for_buffer(self, buffer): #@ReservedAssignment
        '''
        Возвращает информацию для временного файла, в который пишется фотография.
        @param buffer: file
        @return: Stat
        '''
        info = fuse.Stat()
        file_stats = os.stat(buffer.name)
        info.st_mode = stat.S_IFREG | self._get_access_mode(False)
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
        path = self._prepare_path(path)
        if not path:
            return self._getattr_for_root()
        path_info = self._parse_path(path)
        if path_info.album:
            logger.debug('%s is album', path)
            return self._getattr_for_album(path_info.album)
        if path_info.photo:
            logger.debug('%s is photo', path)
            return self._getattr_for_photo(path_info.photo)
        if path_info.buffer:
            logger.debug('%s is buffer', path)
            return self._getattr_for_buffer(path_info.buffer)
        logger.debug('no resource on %s found', path)
        return -errno.ENOENT
    
    @_log_exception
    def chmod(self, path, mode):
        '''
        Изменяет права доступа.
        '''
    
    @_log_exception
    def mkdir(self, path, mode):
        '''
        Создает директорию.
        '''
        logger.debug('creating directory %s', path)
        path = self._prepare_path(path)
        path_info = self._parse_path(path)
        if path_info.album or path_info.photo:
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
        path = self._prepare_path(path)
        if not path:
            for album in album_list.albums.values():
                yield fuse.Direntry(album.title)
        else:
            album = album_list.albums[path]
            for photo in album.photos.values():
                yield fuse.Direntry(photo.title)
                
    @_log_exception
    def rmdir(self, path):
        '''
        Удаляет директорию.
        '''
        logger.debug('removing directory %s', path)
        if not self._is_removing_allowed():
            logger.debug('removing not permitted, see --help')
            return -errno.EPERM
        path = self._prepare_path(path)
        path_info = self._parse_path(path)
        if path_info.album is None:
            return -errno.ENOTDIR
        album_list = AlbumList.get()
        album_list.remove(path_info.album.title)
    
    @_log_exception
    def create(self, path, flags, mode):
        '''
        Создает пустой файл.
        '''
        logger.debug('creating %s with flags %s and mode %s', path, flags, mode)
        path = self._prepare_path(path)
        path_info = self._parse_path(path)
        if path_info.album and path_info.photo:
            logger.warning('resource on %s already exists', path)
            return -errno.EEXIST
        if path_info.buffer:
            logger.warning('there is buffer for %s already', path)
            return -errno.EEXIST
        fileobj = tempfile.NamedTemporaryFile()
        self._buffers[path] = fileobj
        logger.debug('buffer created on %s for %s', fileobj.name, path)
    
    @_log_exception
    def open(self, path, flags): #@ReservedAssignment
        '''
        Вызывается перед попыткой открыть файл.
        '''
        logger.debug('opening %s with flags %s', path, flags)
        path = self._prepare_path(path)
        path_info = self._parse_path(path)
        access = os.O_RDONLY | os.O_WRONLY | os.O_RDWR
        if (flags & access) == os.O_RDONLY:
            if path_info.photo is None:
                logger.warning('no photo found on %s', path)
                return -errno.ENOENT
        if (flags & access) == os.O_WRONLY:
            if path_info.buffer is None:
                logger.warning('buffer for %s not opened yet', path)
                return -errno.EIO
        logger.warning('read or write only permitted on %s', path)
        return -errno.EACCES
        
    @_log_exception
    def read(self, path, size, offset):
        '''
        Возвращает порцию данных из файла.
        '''
        path = self._prepare_path(path)
        path_info = self._parse_path(path)
        photo = path_info.photo
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
        path = self._prepare_path(path)
        path_info = self._parse_path(path)
        if path_info.buffer is None:
            logger.warning('buffer for %s not opened yet', path)
            return -errno.EIO
        fileobj = path_info.buffer
        fileobj.seek(offset)
        fileobj.write(buf)
        return len(buf)
    
    @_log_exception
    def flush(self, path):
        '''
        Заставляет файл сохранить изменения.
        Делаем тут опасное допущение, что метод будет вызван всего один раз.
        В моем Debian Wheezy утилита cp v8.13 делает именно один вызов.
        Почему нельзя сделать все то же самое в методе release? Можно, но тогда cp не будет
        дожидаться завершения выгрузки фотографии на сервер.
        Было бы неплохо придумать, как переместить все в release и заставить cp дождаться
        окончания выгрузки.
        '''
        logger.debug('flushing %s', path)
        path = self._prepare_path(path)
        path_info = self._parse_path(path)
        if path_info.buffer is None:
            logger.warning('buffer for %s not opened yet', path)
            return -errno.EIO
        album_title, photo_title = self._split_path(path)
        album_list = AlbumList.get()
        album = album_list.albums[album_title]
        fileobj = path_info.buffer
        fileobj.flush()
        fileobj.seek(0)
        album.add(photo_title, fileobj.read())
        fileobj.close()
        del self._buffers[path]
    
    @_log_exception
    def release(self, path, fh):
        '''
        Закрывает файл.
        '''
        logger.debug('closing %s', path)
        
    @_log_exception
    def unlink(self, path):
        '''
        Удаляет файл.
        '''
        logger.debug('removing file %s', path)
        if not self._is_removing_allowed():
            logger.debug('removing not permitted, see --help')
            return -errno.EPERM
        path = self._prepare_path(path)
        path_info = self._parse_path(path)
        if path_info.album:
            return -errno.EISDIR
        if path_info.photo is None:
            return -errno.ENOENT
        album_list = AlbumList.get()
        album_title, photo_title = self._split_path(path)
        album = album_list.albums[album_title]
        album.remove(photo_title)


def start():
    '''
    Монтирует директорию и запускает всю FUSE-кухню.
    '''
    set_log_file('filesystem.log')
    set_logger_verbose()
    fuse.fuse_python_api = (0, 2)
    fs = FotkiFilesystem()
    fs.parser.add_option('--allow-removing', action='store_true', dest='is_removing_allowed',
                         help='allow to remove albums and photos')
    fs.parse()
    fs.main()
