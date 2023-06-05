import re
import time

import lyricsgenius


class GeniusService:

    def __init__(self, artist, title):
        self.__genius = lyricsgenius.Genius()
        self.__artist = artist
        self.__title = title

    def fetch_lyrics_from_genius(self):
        print("Fetching lyrics from genius")
        lyrics = None
        song = self.__query_songs(self.__artist, self.__title)
        if song is not None and not self.__similar_artists(self.__artist, song.artist):
            print("Wrong artist. Trying fetching only by title")
            song = self.__query_songs(None, self.__title)
            if song is not None and not self.__similar_artists(self.__artist, song.artist):
                song = None
        if song is not None:
            lyrics = re.sub(r'\[.*]', '', song.lyrics)
            lyrics = [{'text': line, 'start': 0, 'duration': 0} for line in lyrics.split('\n')[1:] if line != '']
            print("Fetched lyrics from genius")
        else:
            print("No lyrics found on genius")
        return lyrics

    def __query_songs(self, artist, title):
        song = None
        no_of_tries = 10
        while no_of_tries > 0:
            try:
                song = self.__genius.search_song(artist=artist, title=title, get_full_info=False)
                return song
            except Exception:
                no_of_tries -= 1
                time.sleep(1)
        if no_of_tries == 0:
            print("Failed to fetch lyrics from genius")
        return song

    def __similar_artists(self, artists1, artists2):
        if artists1 is None or artists2 is None:
            return False
        artists1 = self.__tokenize_artists(artists1)
        artists2 = self.__tokenize_artists(artists2)
        print("ART 1: ", artists1)
        print("ART 2: ", artists2)
        for artist in artists1:
            if artist in artists2:
                return True
        return False

    @staticmethod
    def __tokenize_artists(artists):
        artists = [re.sub(r'\W+', '', artist.strip().lower()) for artist in [artist.strip() for artist in re.split(',|feat\.|featuring|ft\.| x | with | w/ | / | vs |&', artists)]]
        return artists
