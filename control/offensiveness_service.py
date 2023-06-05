import json
import os
import re

import numpy as np

from control.genius_service import GeniusService
# from control.gesture_detection_service import GestureDetectionService
# from control.gesture_detection_service import GestureDetectionService
from control.speech_to_text_service import SpeechToTextService
from control.youtube_service import YoutubeService
from profanity_check import predict_prob, predict


class OffensivenessService:
    __transcripts_dir = os.path.join('temp', 'transcripts')

    def __init__(self, url):
        self.__yt_service = YoutubeService(url)
        self.__genius = GeniusService(self.__yt_service.artist, self.__yt_service.title)
        self.__asr_service = None
        self.__gesture_detection_service = None

        self.__audio_filepath = None
        self.__video_filepath = None
        self.__transcript_filepath = None
        self.__transcript = None

    def start_processing(self):
        self.__audio_filepath, self.__video_filepath = self.__yt_service.download_data_streams()

        # audio_offensiveness = self.__process_audio_stream()
        video_offensiveness = self.__process_video_stream()
        return 0, 0

    def __process_video_stream(self):
        # self.__gesture_detection_service = GestureDetectionService(self.__video_filepath)
        # return self.__gesture_detection_service.get_offensiveness()
        return 0
    def __process_audio_stream(self):
        self.__transcript = self.__extract_transcript()

        if self.__transcript is None:
            return 0
        text = [line['text'] for line in self.__transcript]
        # offs = predict_prob(text)
        offs = predict(text)
        for line, off in zip(text, offs):
            # pass
            print(f'{line} --- {off}')
        return np.mean(offs)

    def __extract_transcript(self):
        transcript = self.__yt_service.get_manual_transcript()
        transcript = None
        if transcript is None:
            transcript = self.__genius.fetch_lyrics_from_genius()
        if transcript is None:
            transcript = self.__yt_service.get_generated_transcript()
        if transcript is None:
            self.__asr_service = SpeechToTextService(self.__audio_filepath)
            transcript = self.__asr_service.extract_transcript()

        if transcript is not None:
            self.__transcript_filepath = self.__save_transcript(transcript)
        else:
            print("No transcript found")
        return transcript

    def __save_transcript(self, transcript):
        filepath = os.path.join(self.__transcripts_dir,
                                f"{os.path.basename(self.__audio_filepath).rsplit('.', 1)[0]}.json")
        with open(filepath, 'w+') as f:
            json.dump(transcript, f, indent=4)
        return filepath
