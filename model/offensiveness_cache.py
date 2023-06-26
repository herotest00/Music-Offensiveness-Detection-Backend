from sqlalchemy import Column, Numeric, Text, Integer
from sqlalchemy.orm import relationship, synonym

from control.database import Base


class OffensivenessCache(Base):
    __tablename__ = 'offensiveness_cache'
    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(Text, unique=True)
    artist = Column(Text)
    title = Column(Text)
    video_offensiveness = Column(Numeric)
    audio_offensiveness = Column(Numeric)
    _images = relationship("Image", cascade="all, delete-orphan", lazy='joined',
                           order_by="asc(Image.id)")
    _lyrics = relationship("Lyrics", cascade="all, delete-orphan", lazy='joined',
                           order_by="asc(Lyrics.id)")

    def __init__(self, url, artist=None, title=None, video_offensiveness=None, audio_offensiveness=None,
                 images=None, lyrics=None):
        self.url = url
        self.artist = artist
        self.title = title
        self.video_offensiveness = video_offensiveness
        self.audio_offensiveness = audio_offensiveness
        self.images = images
        self.lyrics = lyrics

    @property
    def images(self):
        return self._images

    @images.setter
    def images(self, images):
        if images is not None and len(self._images) == 0:
            self._images = images

    @property
    def lyrics(self):
        return self._lyrics

    @lyrics.setter
    def lyrics(self, lyrics):
        if lyrics is not None and len(self._lyrics) == 0:
            self._lyrics = lyrics

    images = synonym('_images', descriptor=images)
    lyrics = synonym('_lyrics', descriptor=lyrics)
