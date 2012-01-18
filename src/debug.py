# encoding=utf8

from dm_yf.fotki import User

user = User()
albums = user.get_albums()
user.add_album('test-test')
