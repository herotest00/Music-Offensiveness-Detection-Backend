from flask import Blueprint, request

off_resource = Blueprint("offensiveness_resource", __name__)


@off_resource.get("/offensiveness")
def get_offensiveness_for_url():
    url = request.args.get("url")
    print(url)
    offensiveness = {'videoOffensiveness': 0.13,
                     'textOffensiveness': 0.93}
    return offensiveness
