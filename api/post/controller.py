from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from flask_api import status
from commons.constants import EOY_TRANSACTION_GSHEET_API_URL

from helpers.gsheet import getWorksheetsFromGsheetId

post_api = Blueprint("post", __name__)


@post_api.route("", methods=["POST"])
# @jwt_required()
def post_create():
    df = getWorksheetsFromGsheetId(EOY_TRANSACTION_GSHEET_API_URL) 
    print(df)
    return jsonify(success=True), status.HTTP_200_OK
