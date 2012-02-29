# encoding=utf8
'''
Классы для работы с atompub.
@author: Mic, 2012
'''

from xml.etree.ElementTree import fromstring, QName

from dm_yf.http import HttpClient
from dm_yf.log import logger

# Пространства имен:
APP_NS = 'http://www.w3.org/2007/app'
ATOM_NS = 'http://www.w3.org/2005/Atom'

def _get_document(url):
    http_client = HttpClient()
    return http_client.request(url)

def _parse_resource_url(node, rel):
    qname = str(QName(ATOM_NS, 'link'))
    return node.find('%s[@rel="%s"]'%(qname, rel)).attrib['href']


class Service(object):

    _services = {}

    @classmethod
    def get(cls, url):
        if url not in cls._services:
            cls._services[url] = cls(url)
        return cls._services[url]

    def __init__(self, url):
        self._url = url

    def _get_resource_url(self, resource_id):
        document = _get_document(self._url)
        root = fromstring(document)
        for node in root.findall('.//%s'%QName(APP_NS, 'collection')):
            if node.attrib['id'] == resource_id:
                return node.attrib['href']
        return None
    
    def _load_resource(self, url):
        document = _get_document(url)
        root = fromstring(document)
        return Resource(root)
    
    def get_resource(self, resource_id):
        logger.debug('loading resource %s for service %s', resource_id, self._url)
        url = self._get_resource_url(resource_id)
        return self._load_resource(url)


class Resource(object):
    
    def __init__(self, node):
        self._resources = None
        self._node = node
        
    def get_node(self):
        return self._node
        
    def _parse_resources(self, root):
        resources = []
        qname = str(QName(ATOM_NS, 'entry'))
        for node in root.findall(qname):
            resource = Resource(node)
            resources.append(resource)
        return resources
    
    def _get_resources(self, rel):
        url = _parse_resource_url(self._node, rel)
        document = _get_document(url)
        root = fromstring(document)
        return self._parse_resources(root)

    def get_resources(self, rel):
        if self._resources is None:
            self._resources = self._get_resources(rel)
        return self._resources
    
    def get_media(self):
        url = _parse_resource_url(self._node, 'edit-media')
        return _get_document(url)
