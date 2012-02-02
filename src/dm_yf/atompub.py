# encoding=utf8
'''
Классы для работы с atompub.
@author: Mic, 2012
'''

from xml.etree.ElementTree import fromstring, tostring, QName

from dm_yf.http import HttpClient
from dm_yf.log import logger

# Пространства имен:
APP_NS = 'http://www.w3.org/2007/app'
ATOM_NS = 'http://www.w3.org/2005/Atom'

class Service(object):
    '''
    Сервис.
    '''
    
    def __init__(self, url):
        '''
        @param url: string
        '''
        self._http_client = HttpClient()
        self._url = url
    
    def _get_document(self):
        '''
        Загружает и возвращает сервисный документ.
        @return: string
        '''
        return self._http_client.request(self._url)
    
    def _parse_collection(self, node):
        '''
        Получает одну коллекцию.
        @param node: Element
        @return: Collection
        '''
        url = node.attrib['href']
        return Collection(url, node)
    
    def _parse_collections(self, document):
        '''
        Получает коллекции из тела документа.
        @param document: string
        @return: list
        '''
        logger.debug('parsing collections for service %s', self._url)
        root = fromstring(document)
        collections = []
        for node in root.findall('.//%s'%QName(APP_NS, 'collection')):
            collection = self._parse_collection(node)
            collections.append(collection)
        logger.debug('got %s collections for service %s', len(collections), self._url)
        return collections
    
    def get_collections(self):
        '''
        Возвращает набор коллекций в сервисе.
        @return: list
        '''
        logger.debug('loading collections for service %s', self._url)
        document = self._get_document()
        return self._parse_collections(document)


class Collection(object):
    '''
    Коллекция
    '''
    
    def __init__(self, url, node):
        '''
        @param url: string
        @param node: Element
        '''
        self._http_client = HttpClient()
        self._url = url
        self._node = node
        
    def get_node(self):
        '''
        Возвращает ноду коллекции.
        @return: Element
        '''
        return self._node

    def _get_document(self):
        '''
        Загружает и возвращает коллекцию.
        @return: string
        '''
        return self._http_client.request(self._url)
    
    def _get_entry_id(self, node):
        '''
        Возвращает идентификатор элемента.
        @param node: Element
        @return: string
        '''
        qname = str(QName(ATOM_NS, 'id'))
        return node.find(qname).text.encode('utf8')
    
    def _get_entry_self_url(self, node):
        '''
        Возвращает собственный адрес элемента. 
        @param node: Element
        @return: string
        '''
        qname = str(QName(ATOM_NS, 'link'))
        return node.find('%s[@rel="self"]'%qname).attrib['href']
    
    def _get_entry_edit_url(self, node):
        '''
        Возвращает адрес для редактирования элемента.
        @param node: Element
        @return: string
        '''
        qname = str(QName(ATOM_NS, 'link'))
        return node.find('%s[@rel="edit"]'%qname).attrib['href']
    
    def _parse_entry(self, node):
        '''
        Получает один элемент.
        @param node: Element
        @return: Entry
        '''
        id = self._get_entry_id(node)
        self_url = self._get_entry_self_url(node)
        edit_url = self._get_entry_edit_url(node)
        return Entry(id, self_url, edit_url, node)
    
    def _parse_entries(self, document):
        '''
        Получает элементы из тела документа.
        @param document: string
        @return: list
        '''
        logger.debug('parsing entries for collection %s', self._url)
        root = fromstring(document)
        entries = []
        qname = str(QName(ATOM_NS, 'entry'))
        for node in root.findall(qname):
            entry = self._parse_entry(node)
            entries.append(entry)
        logger.debug('got %s entries for collection %s', len(entries), self._url)
        return entries
    
    def get_entries(self):
        '''
        Возвращает набор элементов в коллекции.
        @return: list
        '''
        logger.debug('loading entries for collection %s', self._url)
        document = self._get_document()
        return self._parse_entries(document)

    def add_entry(self, node):
        '''
        Добавляет новый элемент и возвращает его.
        @param node: Element
        @return: Entry
        '''
        data = tostring(node)
        headers = {'Content-Type': 'application/atom+xml; charset=utf-8; type=entry'}
        document = self._http_client.request(self._url, data, headers, method='POST')
        node = fromstring(document)
        return self._parse_entry(node)
        
    def delete_entry(self, entry):
        '''
        Удаляет элемент.
        @param entry: Entry
        '''
        url = entry.get_self_url()
        self._http_client.request(url, method='DELETE')


class Entry(object):
    '''
    Элемент.
    '''
    
    def __init__(self, id, self_url, edit_url, node):
        '''
        @param id: string
        @param self_url: string
        @param edit_url: string
        @param node: Element
        '''
        self._http_client = HttpClient()
        self._id = id
        self._self_url = self_url
        self._edit_url = edit_url
        self._node = node
    
    def get_id(self):
        '''
        Возвращает идентификатор элемента.
        @return: string
        '''
        return self._id
    
    def get_self_url(self):
        '''
        Возвращает собственный адрес.
        @return: string
        '''
        return self._self_url
    
    def get_edit_url(self):
        '''
        Возвращает адрес для редактирования.
        @return: string
        '''
        return self._edit_url
    
    def get_node(self):
        '''
        Возвращает ноду элемента.
        @return: Element
        '''
        return self._node

    def _get_document(self):
        '''
        Загружает и возвращает элемент.
        @return: string
        '''
        return self._http_client.request(self._self_url)
    
    def get(self):
        '''
        Возвращает элемент.
        @return: list
        '''
        logger.debug('loading entry %s', self._self_url)
        document = self._get_document()
        print document
        #return self._parse_entries(document)
