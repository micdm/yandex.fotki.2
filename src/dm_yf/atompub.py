# encoding=utf8
'''
Классы для работы с atompub.
@author: Mic, 2012
'''

from xml.etree.ElementTree import fromstring, tostring

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
        for node in root.findall('.//{%s}collection'%APP_NS):
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
    
    def _parse_entry(self, node):
        '''
        Получает один элемент.
        @param node: Element
        @return: Entry
        '''
        url = node.find('{%s}link[@rel="edit"]'%ATOM_NS).attrib['href']
        return Entry(url, node)
    
    def _parse_entries(self, document):
        '''
        Получает элементы из тела документа.
        @param document: string
        @return: list
        '''
        logger.debug('parsing entries for collection %s', self._url)
        root = fromstring(document)
        entries = []
        for node in root.findall('{%s}entry'%ATOM_NS):
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
        Добавляет новый элемент.
        @param node: Element
        '''
        data = tostring(node)
        headers = {'Content-Type': 'application/atom+xml; charset=utf-8; type=entry'}
        self._http_client.request(self._url, data, headers)


class Entry(object):
    '''
    Элемент.
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
        Возвращает ноду элемента.
        @return: Element
        '''
        return self._node

    def _get_document(self):
        '''
        Загружает и возвращает коллекцию.
        @return: string
        '''
        return self._http_client.request(self._url)
    
    def get(self):
        '''
        Возвращает набор элементов в коллекции.
        @return: list
        '''
        logger.debug('loading entry %s', self._url)
        document = self._get_document()
        print document
        #return self._parse_entries(document)
