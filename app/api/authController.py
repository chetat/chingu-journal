from flask_bcrypt import generate_password_hash, check_password_hash
from bson import json_util, ObjectId
from app.api import api
import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as serializer
import json
from flask_jwt_extended import (
    JWTManager, jwt_required,
    create_access_token,
    get_jwt_identity
)
import os
from model import User
from flask import request, jsonify, url_for, abort, current_app

from ExceptionsClasses import (NotFound,BadRequest,UnAuthorized,
                    InternalServerError,Forbiden,ResourceExist,
                    UnprocessableEntity, MethodNotAllowed)


@api.errorhandler(NotFound)
@api.errorhandler(InternalServerError)
@api.errorhandler(BadRequest)
@api.errorhandler(Forbiden)
@api.errorhandler(UnAuthorized)
@api.errorhandler(MethodNotAllowed)
@api.errorhandler(ResourceExist)

def api_error(error):
    """Catch BadRequest exception globally, serialize into JSON, and respond with 400."""
    payload = dict(error.payload or ())
    payload['status'] = error.status_code
    payload['message'] = error.message
    return jsonify(payload), error.status_code

@api.route('/users', methods=['POST'])
def new_user():
    if request.method == 'POST':
        if not request.is_json:
            return jsonify({"msg": "Missing JSON in request"}), 400
        username = request.json.get('username', None)
        email = request.json.get('email', None)
        password = request.json.get('password', None)


        if not email or not username:
            raise BadRequest("Missing email or username parameter")
        if not password:
            raise BadRequest("Missing password parameter")
        
        #Check for existing user
        user = User.objects.filter(email=email).first()
        if user:
            raise ResourceExist("User already exist")
        else:
            hashed_password = generate_password_hash(password).decode('utf-8')

            
            user = User(email=email, username=username,
                        password_hash=hashed_password)

            user.save()
            access_token = create_access_token(
                identity=user.username, expires_delta=datetime.timedelta(minutes=15))
            return jsonify({"token": access_token, "id": user.serialize.get('id')})



@api.route('login', methods=['POST'])
def login_user():
    if not request.is_json:
        raise BadRequest("Missing JSON in request")

    email = request.json.get('email', None)
    password = request.json.get('password', None)

    if not email:
        raise BadRequest("Missing username or phone parameter")
    if not password:
        raise BadRequest("Missing password parameter")
    
    user = User.objects(email=email).first()
    #Check if user QuerySet is returned from database and check password 
    if user is None:
        raise UnAuthorized("invalid email")
    if not check_password_hash(user.password_hash, password):
        raise UnAuthorized("invalid password")
    else:
        access_token = create_access_token(
            identity=user.username, expires_delta=datetime.timedelta(hours=24))
        return jsonify({"token": access_token, "id": user.serialize.get('id')})

@api.route('/users/<id>', methods=['GET'])
#@jwt_required
def get_user(id):
    if not ObjectId.is_valid(id):
        raise UnprocessableEntity("Invalid User Id")
    user = User.objects(id=id).exclude('password_hash').first()
    if user is None:
        raise NotFound("user not found")
    return jsonify(user.serialize)


@api.route('users/<id>', methods=['PUT'])
#@jwt_required
def update_user(id):
    if not ObjectId.is_valid(id):
        raise UnprocessableEntity("Invalid User Id")
    if not request.is_json:
            return BadRequest("Missing JSON in request", 400)
    username = request.json.get('username', None)
    email = request.json.get('email', None)

    user = User.objects(id=id).first()
    if user is None:
        raise NotFound("User not found")
    user.username = username
    user.email = email

    user.save()
    return jsonify(user=user.serialize)
