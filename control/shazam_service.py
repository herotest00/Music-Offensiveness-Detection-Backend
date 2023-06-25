from shazamio import Shazam


class ShazamService:

    def __init__(self, audio_filepath):
        self.__shazam = Shazam()
        self.__audio_filepath = audio_filepath

        self.__track_data = None
        self.__artist = None
        self.__title = None

    async def get_music_metadata(self):
        if self.__track_data is not None:
            return self.__artist, self.__title
        print("Shazamming...")
        metadata = await self.__shazam.recognize_song(self.__audio_filepath)
        print("Shazam done")
        self.__track_data = metadata.get('track', {})
        self.__artist = self.__track_data.get('subtitle')
        self.__title = self.__track_data.get('title')
        return self.__artist, self.__title

    def get_lyrics(self):
        sections_data = self.__track_data.get('sections', [])
        lyrics_data = next((section for section in sections_data if section.get('type') == 'LYRICS'), None)
        lyrics = lyrics_data.get('text') if lyrics_data else None
        return self.__format_lyrics(lyrics)

    @staticmethod
    def __format_lyrics(lyrics):
        if lyrics is None:
            return None
        else:
            return [{'text': line} for line in lyrics if line != '']

