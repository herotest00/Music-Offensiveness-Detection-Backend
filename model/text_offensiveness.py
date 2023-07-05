from sqlalchemy import Column, Text, Integer, Boolean, ForeignKey

from control.database import Base


class Lyrics(Base):
    __tablename__ = 'text_offensiveness'
    id = Column(Integer, primary_key=True, autoincrement=True)
    oc_id = Column(Text, ForeignKey('offensiveness_cache.id'))
    text = Column(Text)
    offensive = Column(Boolean)

    def __init__(self, text, offensive):
        self.text = text
        self.offensive = offensive

    def serialize(self):
        return {
            'text': self.text,
            'offensive': self.offensive
        }
