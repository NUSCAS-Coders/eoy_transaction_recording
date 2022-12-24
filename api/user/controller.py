from typing import List
from flask import Blueprint, json, jsonify, request
from flask_cors import cross_origin
from api.user.service import read_all_user, read_one_user, update_user_password,update_users
from commons.GlobalState import GlobalState
from commons.constants import EOY_TRANSACTION_GSHEET_API_URL
from config.db import db
from helpers.gsheet import getWorksheetsFromGsheetId
from models.Artist import Artist, Transaction
from .models.user import User
from .service import create_user
from flask_api import status
import re
import string

user_api = Blueprint("user", __name__)

artistIdDict = {
    'A': 1,
    'B': 2,
    'C': 3,
    'D': 4,
    'E': 5,
    'F': 6,
    'G': 7,
    'H': 8,
    'I': 9,
    'J': 10,
    'K': 11,
    'L1': 12,
    'L2': 13,
    'M': 14,
    'N': 15,
    'O': 16,
    'P': 17,
    'Q': 18,
    'R': 19,
    'S': 20,
    'T': 21,
    'U': 22,
    'V': 23,
    'W': 24,
    'X': 25,
    'Y': 26,
    'Z': 27,
    'AA': 28,
    'AB': 29,
    'AC': 30,
    'AD': 31,
}

# Updates artist details
@user_api.route("/update", methods=["GET"], defaults={"sheet_name": None})
@user_api.route("/update/<sheet_name>", methods=["GET"])
def update_artists_info(sheet_name):
    print(sheet_name)
    # if len(GlobalState().artists) == 0:
        # sheet_name = None
    worksheets = getWorksheetsFromGsheetId(EOY_TRANSACTION_GSHEET_API_URL)
    locWorksheet = list(filter(lambda ws: ws.title == 'List of contents', worksheets))[0]

    progWorksheet = list(filter(lambda ws: ws.title == 'Programming Sheet', worksheets))[0]

    discountableMerch = progWorksheet.row_values(6)
    print(discountableMerch)

    for i in range(len(worksheets)):
        worksheet = worksheets[i]
        if re.match(r'\b[A-Z]+\b', worksheet.title) and (sheet_name is None or worksheet.title == sheet_name):
            try:
                artistCount = artistIdDict[worksheet.title]
                print("TITLE: ", worksheet.title)
                print(worksheet.cell(2, 3).value)

                # A first update or refresh is performed
                if sheet_name is None and worksheet.title in GlobalState().artists.keys():
                    continue

                artist = \
                    Artist(
                        locWorksheet.cell(artistCount, 1).value,
                        worksheet.title,
                        worksheet
                    )

                artist.updateWorksheet(worksheet, discountableMerch)

                GlobalState().artists[worksheet.title] = artist
            except Exception as e:
                print(e)
                i -= 1


    for artistName, artist in GlobalState().artists.items():
        print(artistName, artist.artistName, artist.merchMap)

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

@user_api.route("/<artistId>/merch/id", methods=["GET"])
def get_read_merch_id(artistId):
    artist = GlobalState().artists[artistId]
    payload = *[{
        "label": f"{v.artistId}{v.merchId}",
        "value": f"{v.artistId}{v.merchId}"
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
