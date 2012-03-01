# encoding=utf8

from dm_yf.models import AlbumList

def print_photos():
    album_list = AlbumList.get()
    for album in album_list.get_albums():
        print album
        for photo in album.get_photos():
            print photo

def add_album():
    album_list = AlbumList.get()
    album_list.add_album()


add_album()
