from flask import Blueprint, json, jsonify, request
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
    **{c: ord(c) - ord('A') + 1 for c in string.ascii_uppercase},
    'AA': ord('Z') + 2,
    'AB': ord('Z') + 3,
    'AC': ord('Z') + 4,
    'AD': ord('Z') + 5,
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
                        locWorksheet.cell(artistCount + 1, 1).value,
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
        "value": v.merchId
    } for v in artist.merchMap.values()],
    return (
        jsonify(success=True, data=payload),
        status.HTTP_200_OK,
        {"Content-Type": "application/json"},
    )

@user_api.route("/merch", methods=["POST"])
def update_merch_transaction():
    print(request.json)
    listOfTransactions = map(
        lambda d: Transaction(
            d["artistId"],
            d["merchId"],
            d["qty"],
            d["price"]
        ),
        request.json
    )

    listOfArtistIds = set(list(map(
        lambda d: d["artistId"],
        request.json
    )))

    print(listOfArtistIds)

    artists = filter(lambda a: a.artistId in listOfArtistIds, GlobalState().artists.values())

    for artist in artists:
        print(artist)
        artist.handlePurchase(
            list(filter(
                lambda t: t.artistId == artist.artistId,
                listOfTransactions
            ))
        )
    payload = True

    return (
        jsonify(success=True, data=payload),
        status.HTTP_200_OK,
        {"Content-Type": "application/json"},
    )
