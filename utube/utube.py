import os
import youtube_dl

from urllib import request, parse
from bs4 import BeautifulSoup
from youtube_dl.postprocessor.ffmpeg import FFmpegMetadataPP
from utils import safe_path, exp_backoff


LOCAL_PATH = os.environ.get('LOCAL_PATH')
YOUTUBE_URL = 'https://www.youtube.com'


def progress_hook(d):
    if d['status'] == 'finished':
        print(f"Done downloading {d['filename']}, now converting ...")


class FFmpegMP3MetadataPP(FFmpegMetadataPP):

    def __init__(self, downloader=None, metadata=None):
        self.metadata = metadata or {}
        super(FFmpegMP3MetadataPP, self).__init__(downloader)

    def run(self, information):
        information.update(self.metadata.__dict__)
        return super(FFmpegMP3MetadataPP, self).run(information)


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
        destination = os.path.join(LOCAL_PATH, safe_path(playlist))
        self.download_from_url(url, destination,
                               f'{safe_path(track)}.utube',
                               track=track)

    def download_from_url(self, url, destination, title, track=None):
        def _download(url, ydl_opts, retries=0):
            if retries == 3:
                return
            try:
                with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                    if track:
                        ydl.add_post_processor(FFmpegMP3MetadataPP(ydl, track))
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
                'writethumbnail': True,
                'postprocessors': [
                    {
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    },
                    {
                        'key': 'EmbedThumbnail'
                    }
                ],
                'progress_hooks': [progress_hook],
                'outtmpl': os.path.join(destination, title)
            }

            _download(url, ydl_opts)
