import asyncio
import json
import os
from concurrent.futures import ThreadPoolExecutor

import cv2
import numpy as np
from profanity_check import predict

from control.database import db_session
from control.genius_service import GeniusService
from control.object_detection_service import ObjectDetectionService
# from control.gesture_detection_service import GestureDetectionService
from control.shazam_service import ShazamService
from control.speech_to_text_service import SpeechToTextService
from control.youtube_service import YoutubeService
from model.offensiveness_cache import OffensivenessCache
from model.text_offensiveness import Lyrics
from model.video_offensiveness import Image


class OffensivenessService:
    __transcripts_dir = os.path.join('temp', 'transcripts')

    def __init__(self, url):
        self.__yt_service = YoutubeService(url)
        self.__genius_service = GeniusService()
        self.__shazam_service = None
        self.__asr_service = None
        self.__object_detection_service = None
        # self.__gesture_detection_service = None

        self.__audio_filepath = None
        self.__video_filepath = None
        self.__transcript_filepath = None

        self.__url = self.__yt_service.url
        self.__artist = None
        self.__title = None
        self.__transcript = None

    def start_processing(self):
        video_offensiveness = None
        audio_offensiveness = None
        images = None
        text_off = None
        cached_offensiveness = OffensivenessCache.query.filter_by(url=self.__url).first()

        if cached_offensiveness is not None:
            images, video_offensiveness = cached_offensiveness.images, cached_offensiveness.video_offensiveness
            text_off, audio_offensiveness = cached_offensiveness.lyrics, cached_offensiveness.audio_offensiveness
            if video_offensiveness is not None and audio_offensiveness is not None:
                return float(video_offensiveness), images, float(audio_offensiveness), text_off

        self.__audio_filepath, self.__video_filepath = self.__yt_service.download_data_streams()
        self.__artist, self.__title = self.__get_music_metadata()

        with ThreadPoolExecutor(max_workers=2) as executor:
            if audio_offensiveness is None:
                future_audio = executor.submit(self.__process_audio_stream)
            if video_offensiveness is None:
                future_video = executor.submit(self.__process_video_stream)

            if audio_offensiveness is None:
                text_off, audio_offensiveness = future_audio.result()
            if video_offensiveness is None:
                images, video_offensiveness = future_video.result()

        if cached_offensiveness is None:
            db_session.add(OffensivenessCache(self.__url, self.__artist, self.__title, video_offensiveness,
                                              audio_offensiveness, images, text_off))
        else:
            cached_offensiveness.video_offensiveness = video_offensiveness
            cached_offensiveness.audio_offensiveness = audio_offensiveness
            cached_offensiveness.images = images
            cached_offensiveness.lyrics = text_off
        db_session.commit()

        return float(video_offensiveness), images, float(audio_offensiveness), text_off

    def __process_video_stream(self):
        self.__gesture_detection_service = ObjectDetectionService(self.__video_filepath)
        try:
            images = self.__gesture_detection_service.predict()
            return [Image(np_array_to_bytes(image)) for image in images],\
                len(images) / self.__gesture_detection_service.max_num_images
        except Exception as e:
            print('Error in gesture detection: ', e)
            return None, None

    def __process_audio_stream(self):
        try:
            self.__transcript = self.__extract_transcript()
            if self.__transcript is None:
                print("Couldn't extract transcript")
                return None, None

            text = [line['text'] for line in self.__transcript]
            offs = predict(text)
            return [Lyrics(t, o) for t, o in zip(text, offs)], np.mean(offs)
        except Exception as e:
            print('Error in audio processing: ', e)
            return None, None

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

        if transcript is not None:
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


def np_array_to_bytes(image):
    is_success, buffer = cv2.imencode(".jpg", image)
    return buffer.tobytes()
