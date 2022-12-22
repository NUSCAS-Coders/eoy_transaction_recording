from flask_sqlalchemy import SQLAlchemy
from commons.utils import Serializer
from config.db import db


class User(db.Model):
    id = db.Column(db.String, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    password_salt = db.Column(db.String)
    password_hash = db.Column(db.String)
    email = db.Column(db.String(80), unique=True, nullable=False)

    def __repr__(self):
        return f"<User {self.username}>"

    def serialize(self):
        return Serializer.serialize(self)


