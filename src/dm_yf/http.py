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
    
    def _get_headers(self):
        '''
        Возвращает заголовки для запроса (в частности, для авторизации).
        @return: string
        '''
        headers = {}
        headers['Authorization'] = 'OAuth %s'%OAuth.get_token()
        return headers
    
    def request(self, url):
        '''
        Выполняет запрос и возвращает тело ответа.
        @param url: string
        @return: string
        '''
        logger.debug('loading url %s', url)
        headers = self._get_headers()
        request = Request(url, headers=headers)
        response = urlopen(request).read()
        logger.debug('%s bytes loaded from url %s', len(response), url)
        return response
