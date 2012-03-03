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

def add_photo():
    album_list = AlbumList.get()
    albums = album_list.get_albums()
    album = albums[0]
    album.add_photo('foobar', '/home/mic/downloads/4c6a1bd323ddd673d4ac085242fea2e3.jpg')


#add_photo()
print_photos()
