# encoding=utf8

from dm_yf.loaders import AlbumListLoader
from dm_yf.fotki import Album
from dm_yf.stores import AlbumListStore

album_list = AlbumListLoader().load()
album = Album.create('new_album')
album_list.add(album)
AlbumListStore(album_list).store()
