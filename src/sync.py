#!/usr/bin/python
# encoding=utf8
'''
Скрипт для синхронизации.
@author: Mic, 2012
'''

import sys

from dm_yf.log import set_logger_verbose
from dm_yf.synchronizer import Synchronizer

def run():
    '''
    Запускает синхронизацию.
    '''
    if len(sys.argv) == 1:
        print 'Usage: %s [--verbose] <path_to_output_directory>'%sys.argv[0]
        return
    if '--verbose' in sys.argv:
        set_logger_verbose()
    path_to_output_directory = sys.argv[1]
    synchronizer = Synchronizer(path_to_output_directory)
    synchronizer.run()

run()
