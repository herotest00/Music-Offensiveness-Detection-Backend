from sqlalchemy import Column, Text, Numeric

from control.database import Base


class OffensivenessLog(Base):
    __tablename__ = 'offensiveness_logs'
    url = Column(Text, primary_key=True)
    artist = Column(Text)
    title = Column(Text)
    video_offensiveness = Column(Numeric)
    audio_offensiveness = Column(Numeric)

    def __init__(self, url, artist=None, title=None, video_offensiveness=None, audio_offensiveness=None):
        self.url = url
        self.artist = artist
        self.title = title
        self.video_offensiveness = video_offensiveness
        self.audio_offensiveness = audio_offensiveness
