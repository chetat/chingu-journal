
from flask import Flask, jsonify
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from . import Config
import os
import secrets
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity
)

jwt = JWTManager()
bcrypt = Bcrypt()


def create_app(config_filname):
    # App init was here
    app = Flask(__name__)
    app.config.from_pyfile('Config.py')
    app.config['JWT_SECRET_KEY'] = os.environ['SECRET_KEY']

    initialize_extensions(app)
    register_blueprints(app)
    return app

def initialize_extensions(app):
    bcrypt.init_app(app)
    jwt.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})


def register_blueprints(app):
    from app.api import api
    app.register_blueprint(api)



