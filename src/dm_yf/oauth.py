# encoding=utf8

from httplib import HTTPSConnection
import json
from urllib import urlencode

from settings import CLIENT_ID, CLIENT_SECRET, TOKEN

class OAuth(object):
    '''
    Класс для OAuth-авторизации.
    '''
    
    _token = None
    
    @classmethod
    def get_auth_url(cls):
        '''
        Возвращает адрес, где нужно получить код.
        @return: string
        '''
        return 'https://oauth.yandex.ru/authorize?response_type=code&client_id=%s'%CLIENT_ID
    
    @classmethod
    def _get_loaded_token(cls):
        '''
        Возвращает уже загруженный токен.
        @return: string
        '''
        if TOKEN:
            return TOKEN
        if cls._token:
            return cls._token
        return None
    
    @classmethod
    def _load_token(cls, auth_code):
        '''
        Загружает новый токен.
        @param auth_code: string
        @return: string
        '''
        if auth_code is None:
            raise Exception('auth code must be set')
        connection = HTTPSConnection('oauth.yandex.ru')
        body = urlencode({
            'grant_type': 'authorization_code',
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'code': auth_code 
        })
        connection.request('POST', '/token', body)
        response = connection.getresponse().read()
        result = json.loads(response)
        return result['access_token']
    
    @classmethod
    def get_token(cls, auth_code=None):
        '''
        Получает токен для указанного кода.
        @return: string
        '''
        token = cls._get_loaded_token()
        if token is not None:
            return token
        cls._token = cls._load_token(auth_code)
        return cls._token
