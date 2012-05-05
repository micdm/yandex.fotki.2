# encoding=utf8
'''
Полезные функции.
@author: Mic, 2012
'''

from time import mktime

def to_megabytes(size):
    '''
    Переводит байты в мегабайты.
    @param size: int
    @return: float
    '''
    return round(float(size) / 2**20, 2)


def to_timestamp(datetime):
    '''
    Переводит дату и время в метку времени.
    @param datetime: datetime
    @return: int
    '''
    return mktime(datetime.utctimetuple())
