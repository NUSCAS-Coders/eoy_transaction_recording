from api.account.models.account import Account
from api.user.models.user import User
from config.db import db


from flask import Blueprint, jsonify, request
from flask_api import status
def read_all_user(
    **kwargs
):
    user = Account.query.all()


    res = list(map(
        lambda u: u.serialize(),
        user
    ))


    # for i in user:
    #     i['id'] = str(i['id'])

    return( jsonify(
        success=True,
        data=res
    ), status.HTTP_200_OK)

def update_user(
    Username: str, FirstName: str, LastName: str, Email: str, Address: str, id: str
) -> User:
    user = User.query.filter_by(id = user.id).first()

    user = User(
        Username=Username,
        FirstName=FirstName,
        LastName=LastName,
        Email=Email,
        Address=Address,
        id=id
    )
    db.session.commit()
    # user = User(
    #     username=username,
    #     password_salt=password_salt,
    #     password_hash=password_hash,
    #     email=email,
    #     id=id,
    # )
    # db.session.add(user)
    # db.session.commit()
    return user


