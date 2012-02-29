# encoding=utf8
'''
Обмен данными с сервером.
@author: Mic, 2012
'''

from xml.etree.ElementTree import fromstring, QName

from dm_yf.http import HttpClient
from dm_yf.log import logger

# Пространства имен:
APP_NS = 'http://www.w3.org/2007/app'
ATOM_NS = 'http://www.w3.org/2005/Atom'
FOTKI_NS = 'yandex:fotki'

def _get_document(url):
    '''
    Загружает документ по указанному адресу.
    @param url: string
    @return: string
    '''
    http_client = HttpClient()
    return http_client.request(url)

def _parse_resource_url(node, rel):
    '''
    Получает адрес ресурса.
    @param node: Element
    @param rel: string
    @return: string
    '''
    qname = str(QName(ATOM_NS, 'link'))
    return node.find('%s[@rel="%s"]'%(qname, rel)).attrib['href']

def _parse_resource(node):
    qname = str(QName(ATOM_NS, 'id'))
    resource_id_node = node.find(qname)
    if resource_id_node is None:
        logger.error('resource id expected to be but not found')
        return None
    resource_id_parts = resource_id_node.text.split(':')
    resource_type = resource_id_parts[4]
    if resource_type == 'albums':
        return AlbumListResource(node)
    if resource_type == 'album':
        return AlbumResource(node)
    if resource_type == 'photo':
        return PhotoResource(node)
    logger.error('unknown resource type "%s"', resource_type)
    return None


class Service(object):
    '''
    Сервис.
    '''

    # Список уже загруженных сервисов:
    _services = {}

    @classmethod
    def get(cls, url):
        '''
        Фабрика сервисов.
        @param url: string
        @return: Service
        '''
        if url not in cls._services:
            cls._services[url] = cls(url)
        return cls._services[url]

    def __init__(self, url):
        '''
        @param url: string
        '''
        self._url = url

    def _get_resource_url(self, resource_id):
        '''
        Возвращает адрес ресурса с указанным идентификатором.
        @param resource_id: string
        @return: string
        '''
        document = _get_document(self._url)
        root = fromstring(document)
        for node in root.findall('.//%s'%QName(APP_NS, 'collection')):
            if node.attrib['id'] == resource_id:
                return node.attrib['href']
        return None
    
    def _load_resource(self, url):
        '''
        Загружает ресур по указанному адресу.
        @param url: string
        @return: string
        '''
        document = _get_document(url)
        root = fromstring(document)
        return _parse_resource(root)
    
    def get_resource(self, resource_id):
        '''
        Возвращает ресурс с указанным идентификатором.
        @param resource_id: string
        @return: Resource
        '''
        logger.debug('loading resource %s for service %s', resource_id, self._url)
        url = self._get_resource_url(resource_id)
        return self._load_resource(url)


class Resource(object):
    '''
    Ресурс.
    '''
    
    def __init__(self, node):
        '''
        @param node: Element
        '''
        self._resources = None
        self._node = node
        
    def _get_node_by_name(self, name):
        '''
        Возвращает элемент по имени тега.
        @param name: string
        @return: string
        '''
        qname = str(QName(ATOM_NS, name))
        return self._node.find(qname)
        
    def _parse_resources(self, root):
        '''
        Разбирает список ресурсов.
        @param root: Element
        @return: list
        '''
        resources = []
        qname = str(QName(ATOM_NS, 'entry'))
        for node in root.findall(qname):
            resource = _parse_resource(node)
            resources.append(resource)
        return resources
    
    def _get_resources(self, rel):
        '''
        Загружает список ресурсов.
        @param rel: string
        @return: list
        '''
        url = _parse_resource_url(self._node, rel)
        document = _get_document(url)
        root = fromstring(document)
        return self._parse_resources(root)

    def get_resources(self, rel):
        '''
        Возвращает список ресурсов, содержащихся в данном.
        @param rel: string
        @return: list
        '''
        if self._resources is None:
            self._resources = self._get_resources(rel)
        return self._resources


class AlbumListResource(Resource):
    '''
    Ресурс списка альбомов.
    '''


class AlbumResource(Resource):
    '''
    Ресурс альбома.
    '''
    
    def get_title(self):
        '''
        Возвращает название альбома.
        @return: string
        '''
        title_node = self._get_node_by_name('title')
        if title_node is None:
            logger.error('album title not found')
            return None
        return title_node.text.encode('utf8')
    
    def get_image_count(self):
        '''
        Возвращает количество фотографий в альбоме без их предварительной загрузки.
        @return: int
        '''
        qname = str(QName(FOTKI_NS, 'image-count'))
        image_count_node = self._node.find(qname)
        if image_count_node is None:
            logger.error('image count not found')
            return None
        return int(image_count_node.attrib['value'])


class PhotoResource(Resource):
    '''
    Ресурс фотографии.
    '''
    
    def get_title(self):
        '''
        Возвращает название фотографии.
        @return: string
        '''
        title_node = self._get_node_by_name('title')
        if title_node is None:
            logger.error('photo title not found')
            return None
        return title_node.text.encode('utf8')

    def get_size(self):
        '''
        Возвращает размер фотографии в байтах.
        @return: int
        '''
        qname = str(QName(FOTKI_NS, 'img'))
        img_node = self._node.find('%s[@size="orig"]'%qname)
        if img_node is None:
            logger.error('image size value not found')
            return None
        return int(img_node.attrib['bytesize'])

    def get_content(self):
        '''
        Возвращает прикрепленное медиа-содержимое.
        @return: string
        '''
        content_node = self._get_property('content')
        if content_node is None:
            logger.error('attached media not found')
            return None
        url = content_node.attrib['src']
        return _get_document(url)
