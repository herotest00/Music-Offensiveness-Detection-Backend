import json

from flask import Blueprint, request

off_resource = Blueprint("offensiveness_resource", __name__)


@off_resource.get("/offensiveness")
def get_offensiveness_for_url():
    url = request.args.get("url")
    offensiveness = {'videoOffensiveness': 0.13,
                     'textOffensiveness': 0.93}
    return offensiveness


@off_resource.errorhandler(Exception)
def handle_server_exception(e):
    response = e.get_response()
    response.data = json.dumps({
        "code": e.code,
        "message": e.description,
    })
    response.content_type = "application/json"
    return response
