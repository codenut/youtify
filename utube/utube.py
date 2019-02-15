import os
import youtube_dl

from .exceptions import VideoNotFoundException
from youtube_dl.postprocessor.ffmpeg import FFmpegMetadataPP
from utils import safe_path, exp_backoff
from googleapiclient.discovery import build


LOCAL_PATH = os.environ.get('LOCAL_PATH')
YOUTUBE_URL = 'https://www.youtube.com'
DEVELOPER_KEY = os.environ.get('YOUTUBE_DEVELOPER_KEY')
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'


youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                developerKey=DEVELOPER_KEY)


def progress_hook(d):
    if d['status'] == 'finished':
        print(f"Done downloading {d['filename']}, now converting ...")


class FFmpegMP3MetadataPP(FFmpegMetadataPP):

    def __init__(self, downloader=None, metadata=None):
        self.metadata = metadata or {}
        super(FFmpegMP3MetadataPP, self).__init__(downloader)

    def run(self, information):
        information.update(self.metadata)
        return super(FFmpegMP3MetadataPP, self).run(information)


class Utube:
    def _get_url(self, track):
        search_response = youtube.search().list(
            q=str(track),
            part='id',
            type='video',
            maxResults=1
        ).execute()
        if len(search_response['items']) > 0:
            video_id = search_response['items'][0]['id']['videoId']
            return f'{YOUTUBE_URL}/watch?v={video_id}'
        else:
            raise VideoNotFoundException(f'Video not found {track}')

    def download(self, track, playlist):
        destination = self.mkdir(os.path.join(LOCAL_PATH, safe_path(playlist)))

        outtmpl = os.path.join(destination, f'{safe_path(track)}.utube')
        if self.is_file(outtmpl, 'mp3'):
            print(f'File already downloaded {outtmpl}. Skipping...')
        else:
            try:
                url = self._get_url(track)
                metadata = track.__dict__
                self.download_from_url(url, outtmpl=outtmpl, metadata=metadata)
            except VideoNotFoundException as ex:
                print(ex)

    def download_from_url(self, url, outtmpl=None, metadata=None):
        def _download(url, ydl_opts, retries=0):
            if retries == 3:
                return
            try:
                with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                    if metadata:
                        ydl.add_post_processor(
                            FFmpegMP3MetadataPP(ydl, metadata))
                    ydl.download([url])
            except Exception as ex:
                print(ex)
                exp_backoff(retries)
                _download(url, ydl_opts, retries + 1)

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
        }
        if outtmpl:
            ydl_opts['outtmpl'] = outtmpl

        _download(url, ydl_opts)

    def is_file(self, f, ext=None):
        if ext:
            f = f'{os.path.splitext(f)[0]}.{ext}'
        return os.path.isfile(f)

    def mkdir(self, path):
        if not os.path.exists(path):
            os.makedirs(path)
        return path
