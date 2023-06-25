import os

from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS

from api.offensiveness_resource import off_resource
from control.database import db_session, init_db

app = Flask(__name__)

# load config
load_dotenv('.env')

# load db
init_db()

# expose endpoints
app.register_blueprint(off_resource)


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


# CORS
CORS(app, resources={r'/*': {'origins': os.environ['CORS_ALLOWED_ORIGINS']}})
