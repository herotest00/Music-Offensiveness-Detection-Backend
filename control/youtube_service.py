import asyncio
import os
import random
import re
import string

import requests
from bs4 import BeautifulSoup
from pytube import YouTube
from youtube_title_parse import get_artist_title
from youtube_transcript_api import YouTubeTranscriptApi

from control.shazam_service import ShazamService


class YoutubeService:
    __audio_dir = os.path.join('temp', 'audio')
    __video_dir = os.path.join('temp', 'video')

    __illegal_filename_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']

    def __init__(self, url):
        self.__yt = YouTube(url)
        self.__url = self.__yt.watch_url

    def download_data_streams(self):
        filename = self.__generate_filename()

        video_streams = self.__yt.streams.filter(progressive=False, only_video=True).order_by('resolution').desc()
        video_stream = None
        for stream in video_streams:
            if int(stream.resolution.rstrip('p')) <= 1080:
                video_stream = stream
                break
        video_extension = 'webm' if video_stream.mime_type == 'video/webm' else 'mp4'
        video_stream.download(output_path=self.__video_dir, filename=f"{filename}.{video_extension}")
        video_filepath = os.path.join(self.__video_dir, f"{filename}.{video_extension}")

        audio_stream = self.__yt.streams.filter(progressive=False, only_audio=True).order_by('bitrate').desc().first()
        audio_extension = 'webm' if audio_stream.mime_type == 'audio/webm' else 'mp4'
        audio_stream.download(output_path=self.__audio_dir, filename=f"{filename}.{audio_extension}")
        audio_filepath = os.path.join(self.__audio_dir, f"{filename}.{audio_extension}")

        return audio_filepath, video_filepath

    def get_manual_transcript(self):
        print("Fetching manual youtube transcript")
        transcript = None
        try:
            available_transcripts = YouTubeTranscriptApi.list_transcripts(self.__yt.video_id)
            transcript = available_transcripts.find_manually_created_transcript(['en']).fetch()
            transcript = self.__format_transcript(transcript)
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
            transcript = self.__format_transcript(transcript)
            print("Fetched generated youtube transcript")
        except Exception:
            print("No generated transcript found on youtube")
        return transcript

    @staticmethod
    def __format_transcript(transcript):
        for entry in transcript:
            entry['text'] = re.sub(r'[\n\t♪]+', ' ', entry['text']).strip()
        return transcript

    def __generate_filename(self):
        filename = self.scrape_youtube(self.__url).replace(' ', '_')
        return self.__sanitize_filename(filename)

    def __sanitize_filename(self, filename):
        return filename.translate(str.maketrans('', '', ''.join(self.__illegal_filename_chars)))

    def get_song_metadata(self):
        title = self.scrape_youtube(self.__url)
        if get_artist_title(title) is None:
            return None, None
        return get_artist_title(title)

    @staticmethod
    def scrape_youtube(url):
        r = requests.get(url)
        soup = BeautifulSoup(r.text, "html.parser")
        title = soup.find("title").string.replace(" - YouTube", "")
        title = re.sub(r'\((?!.*?(feat|ft|feature).*?)\).*?\)', '', title)
        title = re.sub(r'\[(?!.*?(feat|ft|feature).*?)\].*?\]', '', title)
        return title

    @property
    def url(self):
        return self.__url
