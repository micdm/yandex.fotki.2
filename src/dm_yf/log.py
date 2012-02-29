# encoding=utf8
'''
Логирование.
@author: Mic, 2012
'''

from logging import getLogger, DEBUG, StreamHandler, Formatter

formatter = Formatter('%(asctime)s [%(levelname)s] %(message)s')

handler = StreamHandler()
handler.setFormatter(formatter)

logger = getLogger()
logger.addHandler(handler)
logger.setLevel(DEBUG)
