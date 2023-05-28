import json
import os

from control.speech_to_text_service import SpeechToTextService
from control.youtube_service import YoutubeService


class OffensivenessService:
    __transcripts_dir = os.path.join('temp', 'transcripts')

    __audio_filepath = None
    __video_filepath = None
    __transcript_filepath = None
    __transcript = None

    __asr_service = None

    def __init__(self, url):
        self.__yt_service = YoutubeService(url)

    def start_processing(self):
        self.__audio_filepath, self.__video_filepath = self.__yt_service.download_data_streams()

        self.__process_audio_stream()

    def __process_video_stream(self):
        pass

    def __process_audio_stream(self):
        self.__extract_transcript()

    def __extract_transcript(self):
        self.__transcript = self.__yt_service.get_transcript()
        if self.__transcript is None:
            self.__asr_service = SpeechToTextService(self.__audio_filepath)
            self.__transcript = self.__asr_service.extract_transcript()

        self.__transcript_filepath = os.path.join(self.__transcripts_dir,
                                                  f"{os.path.basename(self.__audio_filepath).split('.')[0]}.json")
        with open(self.__transcript_filepath, 'w+') as f:
            json.dump(self.__transcript, f, indent=4)

    def __transcribe_audio(self):
        pass

    def __analyze_text(self):
        pass

    def __analyze_video(self):
        pass
