from typing import List
from flask import Blueprint, json, jsonify, request
from flask_cors import cross_origin
from api.user import service as user_service
from commons.GlobalState import GlobalState
from config.db import db
from helpers.gsheet import getWorksheetsFromGsheetId
from models.Artist import Artist, Transaction
from .models.user import User
from .service import create_user, generateImageImgComponent
from flask_api import status
import re
import string

user_api = Blueprint("user", __name__)



# Updates artist details
@user_api.route("/update", methods=["GET"], defaults={"sheet_name": None})
@user_api.route("/update/<sheet_name>", methods=["GET"])
def update_artists_info(sheet_name):
    user_service.update_artists_info(sheet_name)
    return (
        jsonify(success=True, data="Updated"),
        status.HTTP_200_OK,
        {"Content-Type": "application/json"},
    )


@user_api.route("/", methods=["GET"], defaults={"artistId": None})
@user_api.route("/<artistId>", methods=["GET"])
def get_read(artistId):
    payload = list(map(
        lambda a: a.toJSON(),
        filter(
            lambda a: artistId is None or a.artistId == artistId,
            GlobalState().artists.values()
        )
    ))
    return (
        jsonify(success=True, data=payload),
        status.HTTP_200_OK,
        {"Content-Type": "application/json"},
    )

@user_api.route("/artistIds", methods=["GET"], defaults={"artistId": None})
def get_read_artistIds(artistId):
    payload = list(GlobalState().artists.keys())
    payload = *[{
        "label": f"{a.artistId} - {a.artistName}",
        "value": a.artistId
    } for a in GlobalState().artists.values()],
    return (
        jsonify(success=True, data=payload),
        status.HTTP_200_OK,
        {"Content-Type": "application/json"},
    )

@user_api.route("/<artistId>/merch", methods=["GET"])
def get_read_merch(artistId):
    artist = GlobalState().artists[artistId]
    payload = {k: v.toJSON() for k, v in artist.merchMap.items()},
    return (
        jsonify(success=True, data=payload),
        status.HTTP_200_OK,
        {"Content-Type": "application/json"},
    )

@user_api.route("/<artistId>/merch/<merchId>", methods=["GET"])
def get_merch_given_artistId_and_merchId(artistId, merchId):
    artist = GlobalState().artists[artistId]
    payload = {
        **artist.merchMap[merchId].toJSON(),
        "imageLink": artist.merchMap[merchId].imageLink,
        "embedCode": generateImageImgComponent(artist.merchMap[merchId])
    }
    return (
        jsonify(success=True, data=payload),
        status.HTTP_200_OK,
        {"Content-Type": "application/json"},
    )

@user_api.route("/<artistId>/merch/id", methods=["GET"])
def get_read_merch_id(artistId):
    # user_service.update_artists_info(artistId)
    artist = GlobalState().artists[artistId]


    

    payload = *[{
        "label": f"{v.merchId}",
        "value": f"{v.merchId}",
        "imageLink": v.imageLink,
        "embedCode": generateImageImgComponent(v)
    } for v in filter(
        lambda a: a.currentStock > 0,
        artist.merchMap.values()
    )],

    return (
        jsonify(success=True, data=payload),
        status.HTTP_200_OK,
        {"Content-Type": "application/json"},
    )

@user_api.route("/<artistId>/merch/<merchId>/price", methods=["GET"])
def get_read_merch_price(artistId, merchId):
    # user_service.update_artists_info(artistId)
    artist = GlobalState().artists[artistId]
    merch = artist.merchMap[merchId]
    payload = [
        {
            "label": f"{merch.initialPrice}",
            "value": float(merch.initialPrice[1:])
        }
    ]

    if merch.discountable:
        payload.append(
            {
                "label": f"Giveaway",
                "value": 0
            }
        )
    
    return (
        jsonify(success=True, data=payload),
        status.HTTP_200_OK,
        {"Content-Type": "application/json"},
    )

@user_api.route("/<artistId>/merch/<merchId>/qty/range", methods=["GET"])
def get_read_merch_qty(artistId, merchId):
    # user_service.update_artists_info(artistId)
    artist = GlobalState().artists[artistId]
    merch = artist.merchMap[merchId]
    payload = [
        {
            "label": f"{i}",
            "value": i
        }
    for i in range(1, merch.currentStock+1)]

    return (
        jsonify(success=True, data=payload),
        status.HTTP_200_OK,
        {"Content-Type": "application/json"},
    )

@user_api.route("/merch", methods=["POST"])
def update_merch_transaction():
    print(request.json)
    if request.json is None:
        return (
        jsonify(success=False),
        status.HTTP_500_INTERNAL_SERVER_ERROR,
        {"Content-Type": "application/json"},
    )

    listOfTransactions = map(
        lambda d: Transaction(
            d["artistId"]["value"],
            GlobalState().artists[d["artistId"]["value"]].merchMap[d["merchId"]["value"]],
            d["qty"]["value"],
            d["price"]["value"],
            d
        ),
        request.json
    )

    listOfArtistIds = set(list(map(
        lambda d: d["artistId"]["value"],
        request.json
    )))

    print(listOfArtistIds)

    artists: List[Artist] = list(filter(lambda a: a.artistId in listOfArtistIds, GlobalState().artists.values()))

    savedTransactions = []
    with open('static/transactions.json', 'r') as f:
        if f is not None:
            savedTransactions = json.loads(f.read())
    
    for artist in artists:
        print(artist)
        artist.handlePurchase(
            list(filter(
                lambda t: t.artistId == artist.artistId,
                listOfTransactions
            )),
            savedTransactions
        )


    with open('static/transactions.json', 'w') as f:
        f.write(json.dumps(savedTransactions))

    payload = True

    return (
        jsonify(success=True, data=payload),
        status.HTTP_200_OK,
        {"Content-Type": "application/json"},
    )
