from flask_sqlalchemy import SQLAlchemy
from commons.utils import Serializer
from config.db import db


class User(db.Model):
    
    __tablename__ = 'User'
    
    userID = db.Column(db.String(80), primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80))
    firstName = db.Column(db.String(80))
    lastName = db.Column(db.String(80))
    email = db.Column(db.String(80), unique=True, nullable=False)
    address = db.Column(db.String(80))
    optIntoPhyStatements = db.Column(db.String(80))

    def __repr__(self):
        return f"<User {self.username}>"

    def serialize(self):
        return Serializer.serialize(self)

    def serialize_public(self):
        temp = Serializer.serialize(self)
        del temp["Password"]
        return temp
