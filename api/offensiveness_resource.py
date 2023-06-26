import json
import traceback

from werkzeug.exceptions import HTTPException

from flask import Blueprint, request

from control.offensiveness_service import OffensivenessService

off_resource = Blueprint("offensiveness_resource", __name__)


@off_resource.get("/offensiveness")
def get_offensiveness_for_url():
    url = request.args.get("url")
    service = OffensivenessService(url)
    video_offensiveness, images, audio_offensiveness, text_off = service.start_processing()

    offensiveness = {
        'videoOffensiveness': {
            'score': video_offensiveness,
            'images': [image.serialize() for image in images]
        },
        'audioOffensiveness': {
            'score': audio_offensiveness,
            'text': [text.serialize() for text in text_off]}
    }
    return offensiveness


@off_resource.errorhandler(Exception)
def handle_server_exception(e):
    traceback.print_exc()
    if isinstance(e, HTTPException):
        response = e.get_response()
        response.data = json.dumps({
            "code": e.code,
            "message": e.description,
        })
        response.content_type = "application/json"
        return response
    else:
        return json.dumps({
            "code": 500,
            "message": str(e),
        }), 500
