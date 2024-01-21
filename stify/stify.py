import os

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

USERNAME = os.environ.get('SPOTIFY_USERNAME')
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials())


class Stify:
    def __init__(self):
        self._playlists = None

    @property
    def playlists(self):
        if self._playlists is None:
            self._playlists = sp.user_playlists(USERNAME)
        return [Playlist(playlist) for playlist in self._playlists['items']]


class Playlist:
    def __init__(self, playlist):
        self.id = playlist['id']
        self.name = playlist['name']
        self._tracks = None

    @property
    def tracks(self):
        if self._tracks is None:
            self._tracks = self._get_tracks()
        return self._tracks

    def _get_tracks(self):
        def gen_tracks():
            results = sp.user_playlist(
                USERNAME, self.id, fields="tracks,next")
            tracks = results['tracks']
            print(tracks)

            while tracks:
                for i, track in enumerate(tracks['items']):
                    if track['track']:
                        yield Track(track['track'])
                tracks = sp.next(tracks)

        if self._tracks is not None:
            return self._tracks

        self._tracks = list(gen_tracks())
        return self._tracks

    def update_tracks(self):
        pass


class Track:
    def __init__(self, track):
        self.artist = track['artists'][0]['name']
        self.title = track['name']
        self.album = track['album']['name']
        self.disc_number = track['disc_number']

    def __repr__(self):
        return f'{self.title} - {self.artist}'
