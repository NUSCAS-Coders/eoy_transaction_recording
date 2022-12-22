from flask_sqlalchemy import SQLAlchemy
from commons.utils import Serializer
from config.db import db


class Account(db.Model):
    __tablename__ = 'BankAccount'

    accountID = db.Column(db.Integer, nullable=False, primary_key=True)
    userID = db.Column(db.Integer, nullable=False, primary_key=True)
    accountType = db.Column(db.String(80))
    accountBalance = db.Column(db.String(80))

    def __repr__(self):
        return f"<Account {self.accountID}>"

    def serialize(self):
        return Serializer.serialize(self)


