#!/usr/bin/python
# encoding=utf8
'''
Скрипт для синхронизации.
@author: Mic, 2012
'''

import argparse

from dm_yf.log import set_logger_verbose
from dm_yf.synchronizer import Synchronizer

def _get_args():
    '''
    Возвращает разобранные аргументы командной строки.
    '''
    parser = argparse.ArgumentParser(description='Synchronize remote albums to local space.')
    parser.add_argument('--verbose', required=False, action='store_true', dest='is_verbose', help='show verbose output')
    parser.add_argument('path_to_output_dir', action='store', help='set output directory')
    return parser.parse_args()

def run():
    '''
    Запускает синхронизацию.
    '''
    args = _get_args()
    if args.is_verbose:
        set_logger_verbose()
    synchronizer = Synchronizer(args.path_to_output_dir)
    synchronizer.run()

run()
