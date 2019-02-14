from stify import Stify
from utube import Utube


def run():
    s = Stify()
    utube = Utube()

    for playlist in s.playlists:
        for track in playlist.tracks:
            utube.download(track, playlist.name)


if __name__ == '__main__':
    run()
