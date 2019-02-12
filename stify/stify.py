import os

from spotipy import util, Spotify


SCOPE = 'user-library-read,playlist-read-private,playlist-read-collaborative'
USERNAME = os.environ.get('SPOTIFY_USERNAME')

token = util.prompt_for_user_token(USERNAME, SCOPE)
sp = Spotify(auth=token)


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
        def gen_tracks(tracks):
            for i, track in enumerate(tracks['items']):
                yield Track(track['track'])

        if self._tracks is not None:
            return self._tracks

        results = sp.user_playlist(USERNAME, self.id, fields="tracks,next")
        self._tracks = list(gen_tracks(results['tracks']))
        while results['tracks']['next']:
            self._tracks += list(gen_tracks(sp.next(results['tracks'])))
        return self._tracks

    def update_tracks(self):
        pass


class Track:
    def __init__(self, track):
        self.artist = track['artists'][0]['name']
        self.name = track['name']

    def __repr__(self):
        return f'{self.name} - {self.artist}'