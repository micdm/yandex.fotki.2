# encoding=utf8
'''
Логирование.
@author: Mic, 2012
'''

from logging import getLogger, DEBUG, INFO, StreamHandler, Formatter

formatter = Formatter('%(asctime)s [%(levelname)s] %(message)s')

handler = StreamHandler()
handler.setFormatter(formatter)

logger = getLogger()
logger.addHandler(handler)
logger.setLevel(INFO)

def set_logger_verbose():
    '''
    Заставляет логгер распечатывать отладочную информацию.
    '''
    logger.setLevel(DEBUG)
    logger.debug('logger is now verbose')
