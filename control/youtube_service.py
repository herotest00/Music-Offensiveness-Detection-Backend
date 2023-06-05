import os
import re

import requests
from bs4 import BeautifulSoup
from pytube import YouTube
from youtube_title_parse import get_artist_title
from youtube_transcript_api import YouTubeTranscriptApi


class YoutubeService:
    __audio_dir = os.path.join('temp', 'audio')
    __video_dir = os.path.join('temp', 'video')
    __illegal_filename_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']

    def __init__(self, url):
        self.__yt = YouTube(url)
        self.__artist, self.__title = self.__get_song_metadata(url)

        self.__filename = self.__generate_filename()

    def download_data_streams(self):
        video_filepath = os.path.join(self.__video_dir, f"{self.__filename}.mp4")
        self.__yt.streams.filter(progressive=False, only_video=True, file_extension='mp4') \
            .order_by('resolution').desc().first() \
            .download(output_path=self.__video_dir, filename=f"{self.__filename}.mp4")

        audio_filepath = os.path.join(self.__audio_dir, f"{self.__filename}.webm")
        self.__yt.streams.filter(progressive=False, only_audio=True, file_extension='webm') \
            .order_by('bitrate').desc().first() \
            .download(output_path=self.__audio_dir, filename=f"{self.__filename}.webm")

        return audio_filepath, video_filepath

    def get_manual_transcript(self):
        print("Fetching manual youtube transcript")
        transcript = None
        try:
            available_transcripts = YouTubeTranscriptApi.list_transcripts(self.__yt.video_id)
            transcript = available_transcripts.find_manually_created_transcript(['en']).fetch()
            self.__format_transcript(transcript)
            print("Fetched manual youtube transcript")
        except Exception:
            print("No manual transcript found on youtube")
        return transcript

    def get_generated_transcript(self):
        print("Fetching generated youtube transcript")
        transcript = None
        try:
            available_transcripts = YouTubeTranscriptApi.list_transcripts(self.__yt.video_id)
            transcript = available_transcripts.find_generated_transcript(['en']).fetch()
            self.__format_transcript(transcript)
            print("Fetched generated youtube transcript")
        except Exception:
            print("No generated transcript found on youtube")
        return transcript

    def __sanitize_filename(self, filename):
        return filename.translate(str.maketrans('', '', ''.join(self.__illegal_filename_chars)))

    @staticmethod
    def __format_transcript(transcript):
        for entry in transcript:
            entry['text'] = re.sub(r'[\n\t♪]+', ' ', entry['text']).strip()
        return transcript

    def __generate_filename(self):
        filename = f"{self.__artist.replace(' ', '_')}-{self.__title}".replace(' ', '_')
        return self.__sanitize_filename(filename)

    def __get_song_metadata(self, url):
        title = self.__scrape_youtube(url)
        return get_artist_title(title)

    @staticmethod
    def __scrape_youtube(url):
        r = requests.get(url)
        soup = BeautifulSoup(r.text, "html.parser")
        title = soup.find("title").string.replace(" - YouTube", "")
        title = re.sub(r'\(.*\)|\[.*\]', '', title)
        return title

    @property
    def artist(self):
        return self.__artist

    @property
    def title(self):
        return self.__title
