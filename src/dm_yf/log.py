# encoding=utf8
'''
Логирование.
@author: Mic, 2012
'''

import logging

formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')

handler = logging.StreamHandler()
handler.setFormatter(formatter)

logger = logging.getLogger()
logger.addHandler(handler)
logger.setLevel(logging.INFO)

def set_logger_verbose():
    '''
    Заставляет логгер распечатывать отладочную информацию.
    '''
    logger.setLevel(logging.DEBUG)
    logger.debug('logger is now verbose')


def set_log_file(path):
    '''
    Заставляет логгер писать сообщения в файл.
    @param path: string
    '''
    handler = logging.FileHandler(path)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
