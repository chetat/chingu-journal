from mongoengine import (DateTimeField,StringField,
 BooleanField, EmbeddedDocumentField, connect,
EmbeddedDocument,ReferenceField,Document, EmailField)
from bson import ObjectId
from datetime import datetime
from flask import request, jsonify
import json


connect('journal_db')

class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        elif isinstance(o, EmbeddedDocument):
            return str(o)
        elif isinstance(o, datetime):
            return str(o)
        elif isinstance(o, Document):
            return str(o)
        return json.JSONEncoder.default(self,o)

class User(Document):
    username = StringField(max_length=100)
    phone = StringField(max_length=18)
    email = EmailField(required=True)
    created_at = DateTimeField(required=True,default=datetime.utcnow)
    password_hash = StringField(max_length=500)
    reset_token = StringField(required=True, max_length=500, default="")
    isActive = BooleanField(default=False)
    updated_at = DateTimeField(required=True, default=datetime.utcnow)

    @property
    def serialize(self):
        return {
            "id": JSONEncoder().encode(self.id).strip(r"\""),
            "username": self.username,
            "phone": self.phone,
            "email": self.email,
            "created": self.created_at,
            "updated_at": self.updated_at,
            "isActive": self.isActive
        }

class Note(Document):
    title = StringField(required=True)
    text = StringField(required=True)
    user = ReferenceField(User,required=True)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)

    @property
    def serialize(self):
        return {
        "id":  JSONEncoder().encode(self.id).strip(r"\""),
        "title": self.title,
        "text": self.text,
        "user_id": JSONEncoder().encode(self.user.id).strip(r"\""),
        "created_at": self.created_at,
        "updated_at": self.updated_at
        }