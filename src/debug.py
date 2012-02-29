# encoding=utf8

from dm_yf.models import AlbumList

album_list = AlbumList.get()
for album in album_list.get_albums():
    print album
    for photo in album.get_photos():
        print photo
