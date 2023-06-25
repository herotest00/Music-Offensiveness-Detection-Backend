import asyncio
import json
import os

import numpy as np

from control.database import db_session
from control.genius_service import GeniusService
# from control.gesture_detection_service import GestureDetectionService
from control.shazam_service import ShazamService
from control.speech_to_text_service import SpeechToTextService
from control.youtube_service import YoutubeService
from profanity_check import predict_prob, predict

from model.offensiveness_log import OffensivenessLog


class OffensivenessService:
    __transcripts_dir = os.path.join('temp', 'transcripts')

    def __init__(self, url):
        self.__yt_service = YoutubeService(url)
        self.__genius_service = GeniusService()
        self.__shazam_service = None
        self.__asr_service = None
        self.__gesture_detection_service = None

        self.__audio_filepath = None
        self.__video_filepath = None
        self.__transcript_filepath = None

        self.__url = self.__yt_service.url
        self.__artist = None
        self.__title = None
        self.__transcript = None

    def start_processing(self):
        cached_offensiveness = OffensivenessLog.query.filter_by(url=self.__url).first()
        if cached_offensiveness is not None:
            return float(cached_offensiveness.video_offensiveness), float(cached_offensiveness.audio_offensiveness)

        self.__audio_filepath, self.__video_filepath = self.__yt_service.download_data_streams()
        self.__artist, self.__title = self.__get_music_metadata()

        audio_offensiveness = self.__process_audio_stream()
        # audio_offensiveness = 0
        # video_offensiveness = self.__process_video_stream()
        video_offensiveness = 0

        db_session.add(OffensivenessLog(self.__url, self.__artist, self.__title, video_offensiveness, audio_offensiveness))
        db_session.commit()

        return 0, audio_offensiveness

    def __process_video_stream(self):
        # self.__gesture_detection_service = GestureDetectionService(self.__video_filepath)
        # return self.__gesture_detection_service.get_offensiveness()
        pass

    def __process_audio_stream(self):
        self.__transcript = self.__extract_transcript()

        if self.__transcript is None:
            return 0
        text = [line['text'] for line in self.__transcript]
        # offs = predict_prob(text)
        offs = predict(text)
        for line, off in zip(text, offs):
            # print(f'{line} --- {off}')
            pass
        return np.mean(offs)

    def __extract_transcript(self):
        transcript = self.__shazam_service.get_lyrics()
        if transcript is None:
            transcript = self.__yt_service.get_manual_transcript()
        if transcript is None:
            artist, title = asyncio.run(self.__shazam_service.get_music_metadata())
            transcript = self.__genius_service.fetch_lyrics_from_genius(artist, title)
            if artist in self.__yt_service.scrape_youtube(self.__url) and transcript is not None:
                self.__artist, self.__title = artist, title
            else:
                artist, title = self.__yt_service.get_song_metadata()
                transcript = self.__genius_service.fetch_lyrics_from_genius(artist, title)
                self.__artist, self.__title = artist, title
        if transcript is None:
            transcript = self.__yt_service.get_generated_transcript()
        if transcript is None:
            self.__asr_service = SpeechToTextService(self.__audio_filepath)
            transcript = self.__asr_service.extract_transcript()

        if transcript is None:
            raise Exception("No transcript found")
        else:
            self.__transcript_filepath = self.__save_transcript(transcript)
        return transcript

    def __save_transcript(self, transcript):
        filepath = os.path.join(self.__transcripts_dir,
                                f"{os.path.basename(self.__audio_filepath).rsplit('.', 1)[0]}.json")
        with open(filepath, 'w+') as f:
            json.dump(transcript, f, indent=4)
        return filepath

    def __get_music_metadata(self):
        self.__shazam_service = ShazamService(self.__audio_filepath)
        artist, title = asyncio.run(self.__shazam_service.get_music_metadata())
        if artist is None or title is None:
            artist, title = self.__yt_service.get_song_metadata()
        return artist, title

