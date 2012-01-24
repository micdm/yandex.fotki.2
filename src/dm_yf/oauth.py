# encoding=utf8

from httplib import HTTPSConnection
import json
from urllib import urlencode

from dm_yf.log import logger
from settings import CLIENT_ID, CLIENT_SECRET, TOKEN

class OAuth(object):
    '''
    Класс для OAuth-авторизации.
    '''

    # Токен:
    _token = None
    
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
    def _get_auth_url(cls):
        '''
        Возвращает адрес, где нужно получить код.
        @return: string
        '''
        return 'https://oauth.yandex.ru/authorize?response_type=code&client_id=%s'%CLIENT_ID
    
    @classmethod
    def _load_token(cls):
        '''
        Загружает новый токен.
        @return: string
        '''
        logger.debug('loading token')
        logger.info('please copy an auth code from %s', cls._get_auth_url())
        auth_code = raw_input()
        logger.debug('auth code is %s', auth_code)
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
        token = result['access_token']
        logger.debug('token loaded: %s', token)
        return token
    
    @classmethod
    def get_token(cls):
        '''
        Получает токен для указанного кода.
        @return: string
        '''
        token = cls._get_loaded_token()
        if token is not None:
            return token
        cls._token = cls._load_token()
        logger.info('please put in this token into your settings_local.py: %s', cls._token)
        return cls._token
