import os.path
import json

from flask import request, Response, url_for, send_from_directory
from werkzeug.utils import secure_filename
from jsonschema import validate, ValidationError

from . import models
from . import decorators
from tuneful import app
from .database import session
from .utils import upload_path

songs_schema = {
    "file":
        {"id": {"type": "integer"}
         }
}

@app.route("/api/songs", methods=["GET"])
@decorators.accept("application/json")
def songs_get():

    songs = session.query(models.File).order_by(models.File.id)

    data = json.dumps([song.as_dictionary() for song in songs])
    print(data)
    return Response(data, 200, mimetype="application/json")

@app.route("/api/songs", methods=["POST"])
@decorators.accept("application/json")
@decorators.require("application/json")
def songs_post():
    data = request.json

    try:
        validate(data, songs_schema)
    except ValidationError as error:
        data = {"message": error.message}
        return Response(json.dumps(data), 422, mimetype="application/json")

    song = models.Song(id=data["file"]["id"])
    session.add(song)
    session.commit()

    data = json.dumps(song.as_dictionary())
    headers = {"Location": url_for("songs_get", id=song.id)}
    return Response(data, 201, headers=headers,
                    mimetype="application/json")

@app.route("/api/songs/<int:id>", methods=["POST"])
@decorators.accept("application/json")
@decorators.require("application/json")
def edit_song(id):

    song = session.query(models.File).get(id)

    song.name = request.json["name"]
    song.file = request.json["file"]

    session.commit()

    data = json.dumps(song.as_dictionary())
    headers = {"Location": url_for("song_get", id=song.id)}
    return Response(data, 200, headers=headers,
                    mimetype="application/json")

@app.route("/api/songs/<int:id>/delete", methods=["POST"])
@decorators.accept("application/json")
def delete_song(id):
    song = session.query(models.Song).get(id)
    session.delete(song)
    session.commit()

    data = json.dumps(song.as_dictionary())
    return Response(data, 200, mimetype="application/json")

@app.route("/uploads/<filename>", methods=["GET"])
def uploaded_file(filename):
    return send_from_directory(upload_path(), filename)

@app.route("/api/files", methods=["POST"])
@decorators.require("multipart/form-data")
@decorators.accept("application/json")
def file_post():
    file = request.files.get("file")
    if not file:
        data = {"message": "Could not find file data"}
        return Response(json.dumps(data), 422, mimetype="application/json")

    filename = secure_filename(file.filename)
    db_file = models.File(filename=filename)
    session.add(db_file)
    session.commit()
    file.save(upload_path(filename))

    data = db_file.as_dictionary()
    return Response(json.dumps(data), 201, mimetype="application/json")
