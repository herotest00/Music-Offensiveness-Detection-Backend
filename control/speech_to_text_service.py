import os
import shutil

import demucs.separate
import whisper
from moviepy.audio.io.AudioFileClip import AudioFileClip


class SpeechToTextService:
    __audio_dir = os.path.join('temp', 'audio')
    __demucs_model_name = 'hdemucs_mmi'
    __whisper_model_name = 'small'

    def __init__(self, filepath):
        self.__set_file_path(filepath)
        self.__whisper_model = whisper.load_model(self.__whisper_model_name)

    def extract_transcript(self):
        self.__convert_to_wav()
        self.__extract_vocals()

        print("Transcribing...")
        transcript = self.__whisper_model.transcribe(self.__filepath)
        print("Transcription complete.")

        return self.__filter_transcript(transcript['segments'])

    def __convert_to_wav(self):
        wav_filepath = os.path.join(self.__audio_dir, f"{self.__filename.split('.')[0]}.wav")

        audio = AudioFileClip(self.__filepath)
        audio.write_audiofile(wav_filepath)

        self.__set_file_path(wav_filepath)

    def __extract_vocals(self):
        demucs.separate.main(["--two-stems", "vocals", "-n", self.__demucs_model_name, "-j", "2",
                              "-o", self.__audio_dir, self.__filepath])
        shutil.move(os.path.join(self.__audio_dir, self.__demucs_model_name,
                                 f"{self.__filename.split('.')[0]}", 'vocals.wav'), self.__filepath)
        shutil.rmtree(os.path.join(self.__audio_dir, self.__demucs_model_name), ignore_errors=True)

    def __set_file_path(self, filepath):
        self.__filepath = filepath
        self.__filename = os.path.basename(filepath)

    @staticmethod
    def __filter_transcript(transcript):
        filtered_data = []
        for item in transcript:
            filtered_data.append({key: item[key] for key in ['text', 'start', 'end']})
        return filtered_data

