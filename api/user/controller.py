from typing import List
from flask import Blueprint, json, jsonify, request
from flask_cors import cross_origin
from gspread.client import APIError
from api.user import service as user_service
from flask_api import status

user_api = Blueprint("user", __name__)



# Updates artist details
@user_api.route("/update", methods=["GET"], defaults={"sheet_name": None})
@user_api.route("/update/<sheet_name>", methods=["GET"])
def update_artists_info(sheet_name):
    try:
        user_service.update_artists_info(sheet_name)
    except APIError as e:
        return (
            jsonify(success=False, data=e.response.json()),
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            {"Content-Type": "application/json"},
        ) 
    return (
        jsonify(success=True, data="Updated"),
        status.HTTP_200_OK,
        {"Content-Type": "application/json"},
    )



@user_api.route("/", methods=["GET"], defaults={"artistId": None})
@user_api.route("/<artistId>", methods=["GET"])
def get_read(artistId):

    try:
        payload = user_service.getArtist(artistId)

    except APIError as e:
        return (
            jsonify(success=False, data=e.response.json()),
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            {"Content-Type": "application/json"},
        ) 


    return (
        jsonify(success=True, data=payload),
        status.HTTP_200_OK,
        {"Content-Type": "application/json"},
    )

@user_api.route("/artistIds", methods=["GET"])
def get_read_artistIds():

    try:
        payload = user_service.getAllArtistIds()

    except APIError as e:
        return (
            jsonify(success=False, data=e.response.json()),
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            {"Content-Type": "application/json"},
        ) 

    return (
        jsonify(success=True, data=payload),
        status.HTTP_200_OK,
        {"Content-Type": "application/json"},
    )

@user_api.route("/<artistId>/merch", methods=["GET"])
def get_read_merch(artistId):

    try:
        payload = user_service.getAllArtistMerch(
            artistId
        )

    except APIError as e:
        return (
            jsonify(success=False, data=e.response.json()),
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            {"Content-Type": "application/json"},
        ) 
    return (
        jsonify(success=True, data=payload),
        status.HTTP_200_OK,
        {"Content-Type": "application/json"},
    )

@user_api.route("/<artistId>/merch/<merchId>", methods=["GET"])
def get_merch_given_artistId_and_merchId(artistId, merchId):

    try:
        payload = user_service.getMerch(
            artistId, merchId
        )

    except APIError as e:
        return (
            jsonify(success=False, data=e.response.json()),
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            {"Content-Type": "application/json"},
        )

    return (
        jsonify(success=True, data=payload),
        status.HTTP_200_OK,
        {"Content-Type": "application/json"},
    )

@user_api.route("/<artistId>/merch/id", methods=["GET"])
def get_read_merch_id(artistId):

    try:
        payload = user_service.getAllArtistMerchIdForFormIO(
            artistId
        )

    except APIError as e:
        return (
            jsonify(success=False, data=e.response.json()),
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            {"Content-Type": "application/json"},
        )

    return (
        jsonify(success=True, data=payload),
        status.HTTP_200_OK,
        {"Content-Type": "application/json"},
    )

@user_api.route("/<artistId>/merch/<merchId>/price", methods=["GET"])
def get_read_merch_price(artistId, merchId):

    try:
        payload = user_service.getMerchPrice(
            artistId, merchId
        )

    except APIError as e:
        return (
            jsonify(success=False, data=e.response.json()),
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            {"Content-Type": "application/json"},
        )

    return (
        jsonify(success=True, data=payload),
        status.HTTP_200_OK,
        {"Content-Type": "application/json"},
    )

@user_api.route("/<artistId>/merch/<merchId>/qty/range", methods=["GET"])
def get_read_merch_qty(artistId, merchId):

    try:
        payload = user_service.getListOfAllowedMerchQty(
            artistId, merchId
        )

    except APIError as e:
        return (
            jsonify(success=False, data=e.response.json()),
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            {"Content-Type": "application/json"},
        )

    return (
        jsonify(success=True, data=payload),
        status.HTTP_200_OK,
        {"Content-Type": "application/json"},
    )

@user_api.route("/merch", methods=["POST"])
def update_merch_transaction():

    if request.json is None:
        return (
            jsonify(success=False),
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            {"Content-Type": "application/json"},
        )

    try:
        payload = user_service.updateMerchTransactions(
            request.json
        )

    except APIError as e:
        return (
            jsonify(success=False, data=e.response.json()),
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            {"Content-Type": "application/json"},
        )

    return (
        jsonify(success=True, data=payload),
        status.HTTP_200_OK,
        {"Content-Type": "application/json"},
    )
