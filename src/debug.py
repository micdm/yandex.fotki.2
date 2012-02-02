# encoding=utf8

from dm_yf.loaders import AlbumListLoader
from dm_yf.fotki import Album
from dm_yf.stores import AlbumListStorer

album_list = AlbumListLoader().load()
albums = album_list.get_albums()
print albums

#album = Album.create('foobar')
#album_list.add(album)

for album in albums:
    album_list.delete(album)

AlbumListStorer().store(album_list)
