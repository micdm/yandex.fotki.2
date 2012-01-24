# encoding=utf8

from dm_yf.loaders import AlbumListLoader

album_list = AlbumListLoader().load()
print album_list.get_albums()
