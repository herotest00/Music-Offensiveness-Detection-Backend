import os

from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS

from api.offensiveness_resource import off_resource

app = Flask(__name__)

# expose endpoints
app.register_blueprint(off_resource)

# load env properties
APP_ENV = os.getenv("local") == "True"
if APP_ENV:
    load_dotenv("resources/.env.local")
else:
    load_dotenv("resources/.env.prod")

# CORS
CORS(app, resources={r"/*": {"origins": os.environ["http.cors.allow-origins"]}})
