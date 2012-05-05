# encoding=utf8
'''
Полезные функции.
@author: Mic, 2012
'''

def to_megabytes(size):
    '''
    Переводит байты в мегабайты.
    @param size: int
    @return: float
    '''
    return round(float(size) / 2**20, 2)
