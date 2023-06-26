import base64

from sqlalchemy import Column, Text, Integer, ForeignKey

from control.database import Base


class Image(Base):
    __tablename__ = 'video_offensiveness'
    id = Column(Integer, primary_key=True, autoincrement=True)
    oc_id = Column(Text, ForeignKey('offensiveness_cache.id'))
    image = Column(Text)

    def __init__(self, image):
        self.image = image

    def serialize(self):
        return base64.b64encode(self.image).decode()
