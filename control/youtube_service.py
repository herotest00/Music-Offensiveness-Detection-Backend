import os
import re

from pytube import YouTube
from youtube_transcript_api import YouTubeTranscriptApi


class YoutubeService:
    __audio_dir = os.path.join('temp', 'audio')
    __video_dir = os.path.join('temp', 'video')

    __filename = None

    def __init__(self, url):
        self.__yt = YouTube(url)
        self.__video_id = self.__yt.video_id

    def download_data_streams(self):
        progressive_streams = self.__yt.streams.filter(progressive=True, file_extension='mp4')

        self.__filename = self.__yt.title.replace(' ', '_')
        if self.__yt.author:
            self.__filename = f"{self.__yt.author.replace(' ', '_')}-{self.__filename}"

        if len(progressive_streams) > 0:
            audio_filepath = video_filepath = os.path.join(self.__video_dir, f"{self.__filename}.mp4")
            progressive_streams.order_by('resolution').desc().first() \
                .download(output_path=self.__video_dir, filename=f"{self.__filename}.mp4")
        else:
            video_filepath = os.path.join(self.__video_dir, f"{self.__filename}.mp4")
            self.__yt.streams.filter(progressive=False, only_video=True, file_extension='mp4') \
                .order_by('resolution').desc().first() \
                .download(output_path=self.__video_dir, filename=f"{self.__filename}.mp4")

            audio_filepath = os.path.join(self.__audio_dir, f"{self.__filename}.webm")
            self.__yt.streams.filter(progressive=False, only_audio=True, file_extension='webm') \
                .order_by('bitrate').desc().first() \
                .download(output_path=self.__audio_dir, filename=f"{self.__filename}.webm")

        return audio_filepath, video_filepath

    def get_transcript(self):
        transcript = None
        try:
            available_transcripts = YouTubeTranscriptApi.list_transcripts(self.__video_id)
            transcript = available_transcripts.find_transcript(['en']).fetch()
            self.__sanitize(transcript)
            print("Fetched youtube transcript")
        except Exception:
            print("No transcript found on youtube")
        return transcript

    @staticmethod
    def __sanitize(transcript):
        for entry in transcript:
            entry['text'] = re.sub(r'[\n\t♪]+', ' ', entry['text']).strip()
        return transcript
