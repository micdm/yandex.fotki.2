# encoding=utf8
'''
HTTP-загрузчик. 
@author: Mic, 2012
'''

from time import sleep
import urllib2

from dm_yf.log import logger
from dm_yf.oauth import OAuth


class RequestFailed(Exception):
    '''
    Исключение, выбрасываемое при ошибке запроса.
    '''


class Request(urllib2.Request):
    '''
    HTTP-запрос.
    Умеет использовать методы, отличные от GET и POST.
    '''
    
    @classmethod
    def get(cls, method, *args, **kwargs):
        '''
        Возвращает объект запроса.
        @param method: string
        @return: Request
        '''
        request = cls(*args, **kwargs)
        request._method = method
        return request
    
    def get_method(self):
        return self._method


class HttpClient(object):
    '''
    HTTP-загрузчик.
    '''
    
    # Интервал между повторами запроса (секунды):
    RETRY_INTERVAL = 5
    
    # Количество повторов:
    RETRY_COUNT = 5
    
    def _get_headers(self, headers):
        '''
        Возвращает заголовки для запроса (в частности, для авторизации).
        @return: string
        '''
        if headers is None:
            headers = {}
        headers['Authorization'] = 'OAuth %s'%OAuth.get_token()
        return headers

    def _request(self, url, data, headers, method):
        '''
        Выполняет запрос и возвращает тело ответа.
        @param method: string
        @param url: string
        @param data: string
        @return: string
        '''
        logger.debug('loading url %s', url)
        headers = self._get_headers(headers)
        request = Request.get(method, url, data, headers)
        response = urllib2.urlopen(request).read()
        logger.debug('%s bytes loaded from url %s', len(response), url)
        return response
    
    def request(self, url, data=None, headers=None, method='GET'):
        '''
        Выполняет запрос и возвращает тело ответа.
        Делает бесконечное число попыток, если запрос не проходит.
        @param method: string
        @param url: string
        @param data: string
        @return: string
        '''
        i = 1
        while i:
            try:
                return self._request(url, data, headers, method)
            except Exception as e:
                logger.warning('error occured during request try #%s: %s, retrying in %s seconds', i, e, self.RETRY_INTERVAL)
                sleep(self.RETRY_INTERVAL)
                i += 1
                if i > self.RETRY_COUNT:
                    raise RequestFailed()
