import os

from spotipy import util, Spotify


SCOPE = 'user-library-read,playlist-read-private,playlist-read-collaborative'
USERNAME = os.environ.get('SPOTIFY_USERNAME')


class Auth:
    def __init__(self):
        self._sp = None

    @property
    def sp(self):
        if self._sp is None:
            self._auth()
        return self._sp

    def _auth(self):
        token = util.prompt_for_user_token(USERNAME, SCOPE)
        self._sp = Spotify(auth=token)


auth = Auth()


class Stify:
    def __init__(self):
        self._playlists = None

    @property
    def playlists(self):
        if self._playlists is None:
            self._playlists = auth.sp.user_playlists(USERNAME)
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
            results = auth.sp.user_playlist(USERNAME, self.id,
                                            fields="tracks,next")
            tracks = results['tracks']

            while tracks:
                for i, track in enumerate(tracks['items']):
                    yield Track(track['track'])
                tracks = auth.sp.next(tracks)

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
