import os
import youtube_dl

from urllib import request, parse
from bs4 import BeautifulSoup
from youtube_dl.postprocessor.common import PostProcessor
from utils import safe_path, exp_backoff


LOCAL_PATH = os.environ.get('LOCAL_PATH')
YOUTUBE_URL = 'https://www.youtube.com'


def progress_hook(d):
    if d['status'] == 'finished':
        print(f"Done downloading {d['filename']}, now converting ...")


class SpotifyMetadata(PostProcessor):
    def __init__(self, downloader, track):
        super().__init__(downloader)
        self.track = track

    def run(self, info):
        info['title'] = self.track.name
        info['artist'] = self.track.artist
        return [], info


class Utube:
    def _get_url(self, track):
        query = parse.quote(str(track))
        url = f'{YOUTUBE_URL}/results?search_query={query}'

        response = request.urlopen(url)
        html = response.read()
        soup = BeautifulSoup(html, 'html.parser')

        for vid in soup.findAll(attrs={'class': 'yt-uix-tile-link'}):
            return f"{YOUTUBE_URL}{vid['href']}"

    def download(self, track, playlist):
        url = self._get_url(track)
        destination = os.path.join(LOCAL_PATH, safe_path(playlist),
                                   f'{safe_path(track)}.mp3')
        self.download_from_url(url, destination)

    def download_from_url(self, url, destination):
        def _download(url, ydl_opts, retries=0):
            if retries == 3:
                return
            try:
                with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                    # metadata = SpotifyMetadata(ydl, track)
                    # ydl.add_post_processor(metadata)
                    ydl.download([url])
            except Exception as ex:
                print(ex)
                exp_backoff(retries)
                _download(url, ydl_opts, retries + 1)

        if not os.path.exists(destination):
            os.makedirs(destination)

        if os.path.isfile(destination):
            print(f'File already downloaded {destination}. Skipping...')
        else:
            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'progress_hooks': [progress_hook],
                'outtmpl': destination
            }

            _download(url, ydl_opts)
