# encoding=utf8
'''
HTTP-загрузчик. 
@author: Mic, 2012
'''

from urllib2 import Request, urlopen

from dm_yf.log import logger
from dm_yf.oauth import OAuth

class HttpClient(object):
    '''
    HTTP-загрузчик.
    '''
    
    def _get_headers(self, headers):
        '''
        Возвращает заголовки для запроса (в частности, для авторизации).
        @return: string
        '''
        if headers is None:
            headers = {}
        headers['Authorization'] = 'OAuth %s'%OAuth.get_token()
        return headers
    
    def request(self, url, data=None, headers=None):
        '''
        Выполняет запрос и возвращает тело ответа.
        @param url: string
        @param data: string
        @return: string
        '''
        logger.debug('loading url %s', url)
        headers = self._get_headers(headers)
        request = Request(url, data, headers)
        response = urlopen(request).read()
        logger.debug('%s bytes loaded from url %s', len(response), url)
        return response
