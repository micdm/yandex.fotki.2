# encoding=utf8

from dm_yf.atompub import Entry

entry = Entry('http://api-fotki.yandex.ru/api/users/demerzov/album/134277/')
print entry.get()
