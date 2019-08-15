from app.api import api
from datetime import datetime
import json
from flask_jwt_extended import (
    JWTManager, jwt_required,
    create_access_token,
    get_jwt_identity
)
from mongoengine import Q
import os
from model import Note,User
from flask import request, jsonify, url_for, abort, current_app
import validate_email

from ExceptionsClasses import  (NotFound,BadRequest,UnAuthorized,
                    InternalServerError,Forbiden, MethodNotAllowed)

@api.errorhandler(NotFound)
@api.errorhandler(InternalServerError)
@api.errorhandler(BadRequest)
@api.errorhandler(Forbiden)
@api.errorhandler(UnAuthorized)
@api.errorhandler(MethodNotAllowed)
def api_error(error):
    """Catch BadRequest exception globally, serialize into JSON, and respond with 400."""
    payload = dict(error.payload or ())
    payload['status'] = error.status_code
    payload['message'] = error.message
    return jsonify(payload), error.status_code


@api.route('notes', methods=['GET'])
def get_notes():
    email = request.json.get('email')        
    user = User.objects(email=email).first()
    if not user:
        raise NotFound("User not found")
    notes = Note.objects.filter(user=user.id)
    return jsonify(notes=[note.serialize for note in notes])

@api.route('notes/<id>', methods=['GET'])
def get_note(id):
    note = Note.objects(id=id).first()
    if not note:
        raise NotFound("Note not found")
    return jsonify(note.serialize)

@api.route('notes', methods=['POST'])
def add_note():
    if not request.is_json:
        return BadRequest('Missing JSON request')
    user_email = request.json.get('email')
    title = request.json.get('title')
    note_text = request.json.get('text')

    user = User.objects(email=user_email).first()
    if user is None:
        raise BadRequest("Not Found")
    note = Note(title=title, text=note_text, user=user.id)
    note.save()
    return jsonify(note=note.serialize)

@api.route('notes/<id>', methods=['PUT'])
def update_note(id):
    if not request.is_json:
        raise BadRequest("Missing Json Request")
    title = request.json.get('title')
    text = request.json.get('text')

    note = Note.objects(id=id).first()
    """
    *update_one()* Perform an atomic update on the fields of the first document matched by the query
    *update()* is for actual Document object update
    """
    note.update(
        set__title=title, set__text=text, set__updated_at=datetime.utcnow
    )
    return jsonify({"message": "updated"},note.serialize),201

@api.route('notes/<id>', methods=['DELETE'])
def delete_note(id):
    note = Note.objects(id=id).first()
    if not note:
        raise NotFound("Note not found")
    note.delete()
    return jsonify({"message": "Deleted note with success"})