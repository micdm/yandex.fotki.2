# encoding=utf8

from dm_yf.stores import AlbumListStorer
from dm_yf.user import User

album_list = User.get_album_list()
albums = album_list.get_albums()

album = albums[0]
print album.get_title()
print album.get_photos()

