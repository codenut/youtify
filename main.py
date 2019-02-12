from stify import Stify
from utube import Utube

s = Stify()
utube = Utube()

for playlist in s.playlists:
    for track in playlist.tracks:
        utube.download(track, playlist.name)
