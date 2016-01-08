import os.path

from flask import url_for
from sqlalchemy import Column, Integer, String, Sequence, ForeignKey
from sqlalchemy.orm import relationship

from tuneful import app
from .database import Base, engine


class File(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True)
    filename = Column(String(128))

    songs = relationship("Song", uselist=False,  backref="file")

    def as_dictionary(self):
        return {
            "id": self.id,
            "name": self.filename,
            "path": url_for("uploaded_file", filename=self.filename)
        }
        #file = {
            #"id": self.id,
            #"name": self.name,
        #}
        #return file

class Song(Base):
    __tablename__ = "songs"

    id = Column(Integer, primary_key=True)

    filename = Column(Integer, ForeignKey('files.id'))

    def as_dictionary(self):
        song = {
            "id": self.id,
            "file": {
                "id": self.id,
                "filename": self.filename
            }
        }
        return song



Base.metadata.create_all(engine)
