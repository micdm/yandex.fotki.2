# encoding=utf8

def get_album_entry(collection, album):
    '''
    Находит элемент, соответствующий альбому.
    @param collection: Collection
    @param album: Album
    @return: Entry
    '''
    for entry in collection.get_entries():
        if album.get_id() == entry.get_id():
            return entry
    return None
