from stify import Stify
from utube import Utube
from threading import Thread

from persistence import init_db

IGNORE_PLAYLISTS = ["sleep", "podcast", "meditation", "whitenoise", "jre", "focus", "christian"]


class PlaylistDowloaderThread(Thread):
    def __init__(self, playlist):
        super().__init__()
        self.playlist = playlist
    
    def run(self):
        utube = Utube()
        for track in self.playlist.tracks:
            utube.download(track, self.playlist.name)


def run():
    init_db()
    s = Stify()
    playlists = [playlist for playlist in s.playlists if playlist.name not in IGNORE_PLAYLISTS]
    threads = []

    for playlist in playlists:
        thread = PlaylistDowloaderThread(playlist)
        thread.run()
    #     threads.append(thread)

    # for thread in threads:
    #     thread.join()


if __name__ == '__main__':
    run()
