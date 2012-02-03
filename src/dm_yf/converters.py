# encoding=utf8
'''
Конвертеры данных.
@author: Mic, 2012
'''

from xml.etree.ElementTree import QName

from dm_yf.atompub import ATOM_NS
from dm_yf.fotki import FOTKI_NS, Album, Photo

class AlbumConverter(object):
    
    @classmethod
    def _get_id(cls, node):
        '''
        Возвращает идентификатор альбома.
        @param node: Element
        @return: string
        '''
        qname = str(QName(ATOM_NS, 'id'))
        return node.find(qname).text.encode('utf8')
    
    @classmethod
    def _get_title(cls, node):
        '''
        Возвращает название альбома.
        @param node: Element
        @return: string
        '''
        qname = str(QName(ATOM_NS, 'title'))
        return node.find(qname).text.encode('utf8')
    
    @classmethod
    def _get_photo_count(cls, node):
        '''
        Возвращает количество фотографий в альбоме.
        @param node: Element
        @return: int
        '''
        qname = str(QName(FOTKI_NS, 'image-count'))
        return int(node.find(qname).attrib['value'])
    
    @classmethod
    def from_entry(cls, entry):
        '''
        Собирает альбом из atompub-элемента.
        @param entry: Entry
        @return: Album
        '''
        node = entry.get_node()
        id = cls._get_id(node)
        title = cls._get_title(node)
        photo_count = cls._get_photo_count(node)
        return Album(id, title, photo_count)


class PhotoConverter(object):
    
    @classmethod
    def _get_id(cls, node):
        '''
        Возвращает идентификатор фотографии.
        @param node: Element
        @return: string
        '''
        qname = str(QName(ATOM_NS, 'id'))
        return node.find(qname).text.encode('utf8')
    
    @classmethod
    def _get_title(cls, node):
        '''
        Возвращает название фотографии.
        @param node: Element
        @return: string
        '''
        qname = str(QName(ATOM_NS, 'title'))
        return node.find(qname).text.encode('utf8')
    
    @classmethod
    def from_entry(cls, entry):
        '''
        Собирает фотографию из atompub-элемента.
        @param entry: Entry
        @return: Photo
        '''
        node = entry.get_node()
        id = cls._get_id(node)
        title = cls._get_title(node)
        return Photo(id, title)
