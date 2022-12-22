from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from flask_api import status
from api.account.service import (
    read_all_user
)

account_api = Blueprint("account", __name__)

@account_api.route("", methods=["GET"])
# @jwt_required()
def post_get():
    return read_all_user()
