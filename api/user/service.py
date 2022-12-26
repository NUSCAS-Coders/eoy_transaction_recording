from typing import List
from gspread.client import APIError
from api.user.models.user import User
from commons.GlobalState import GlobalState
from commons.constants import OFFSET_SUMMARY_NAME_ROW, OFFSET_TRANSACTION_PARTITION_ROW
from config.db import db
from flask import Blueprint, json, jsonify, request
from flask_api import status
import time

from helpers.gsheet import getWorksheetsFromGsheetId
import string
import os

from models.Artist import Artist, Transaction

import re

artistIdDict = {}
artistNameDict = {}
print(artistIdDict)

def generateImageImgComponent(v):
        if not isinstance(v.imageLink, list):
            v.imageLink = [v.imageLink]

        attributes = list(map(
                lambda l: f"<img src={l} width=\"32\"></img>",
                v.imageLink
            ))
        

        if v.discountable:
            attributes.append(
                "<span class=\"badge badge-info\">Giveaway</span>"
            )
        if "set" in v.merchId.lower():
            attributes.append(
                "<span class=\"badge badge-primary\">Set</span>"
            )


        return " ".join(attributes)
def update_artists_info(sheet_name=None):

    # if len(GlobalState().artists) == 0:
        # sheet_name = None

    mode = os.getenv("MODE").upper()
    worksheets = getWorksheetsFromGsheetId(
        os.getenv(f"DOCID_{mode}"), 
        sheet_name
    )

    locWorksheet = list(filter(lambda ws: ws.title == 'List of contents', worksheets))[0]
    progWorksheet = list(filter(lambda ws: ws.title == 'Programming Sheet', worksheets))[0]
    summaryWorksheet = list(filter(lambda ws: ws.title == 'Summary', worksheets))[0]
    listOfArtistNames = summaryWorksheet.row_values(1)[2:]
    listOfArtistIds = summaryWorksheet.row_values(2)[2:]
    
    GlobalState().artistNameDict = dict(zip(
        listOfArtistIds,
        listOfArtistNames
    ))

    GlobalState().artistIdDict = { a: i-1 for i, a in enumerate(listOfArtistIds)}

    print(artistIdDict)

    discountableMerch = progWorksheet.row_values(6)
    print(discountableMerch)

    i = 0

    while i  < len(worksheets):
        worksheet = worksheets[i]

        if not (re.match(r'\b[A-Z]+[0-9]*\b', worksheet.title) and (sheet_name is None or worksheet.title == sheet_name)):
            i += 1
            continue

        try:
            imageFormula = worksheet.row_values(2, value_render_option='FORMULA')[OFFSET_TRANSACTION_PARTITION_ROW:]

            def resolveFormula(f):
                match = re.search(r'(?<=(IMAGE\(\")).*(?=(\"\)))', f)
                return match.group() if match is not None else re.split(r'\s*,\s*', f)

            imageLinks = list(map(
                lambda f: resolveFormula(f),
                imageFormula
            ))
            artistName = GlobalState().artistNameDict[worksheet.title]
            print("TITLE: ", worksheet.title)
            # print(worksheet.cell(2, 3).value)

            # A first update or refresh is performed
            if sheet_name is None and worksheet.title in GlobalState().artists.keys():
                continue

            # print("NAME: ", summaryWorksheet.cell(1, artistCount + OFFSET_SUMMARY_NAME_ROW).value)
            artist = \
                Artist(
                    artistName,
                    worksheet.title,
                    worksheet,
                    imageLinks
                )

            artist.updateWorksheet(worksheet, discountableMerch)

            for merchId in artist.merchMap.keys():
                newListOfImageLinks = []
                if isinstance(artist.merchMap[merchId].imageLink, list):
                    for l in artist.merchMap[merchId].imageLink:
                        newListOfImageLinks.append(
                            artist.merchMap[l].imageLink
                        ) 
                    artist.merchMap[merchId].imageLink = newListOfImageLinks

            GlobalState().artists[worksheet.title] = artist

        except APIError as e:
            print("Error: ", e, type(e).__name__)
            time.sleep(0.1)
            continue

        i += 1

def getArtist(artistId):
    payload = list(map(
        lambda a: a.toJSON(),
        filter(
            lambda a: artistId is None or a.artistId == artistId,
            GlobalState().artists.values()
        )
    ))
    return payload

def getAllArtistIds():
    payload = list(GlobalState().artists.keys())
    payload = [{
        "label": f"{a.artistId} - {a.artistName}",
        "value": a.artistId
    } for a in GlobalState().artists.values()]
    return payload

def getAllArtistMerch(artistId):
    artist = GlobalState().artists[artistId]
    payload = {k: v.toJSON() for k, v in artist.merchMap.items()},
    return payload

def getMerch(artistId, merchId):
    artist = GlobalState().artists[artistId]
    payload = {
        **artist.merchMap[merchId].toJSON(),
        "imageLink": artist.merchMap[merchId].imageLink,
        "embedCode": generateImageImgComponent(artist.merchMap[merchId])
    }
    return payload

def getAllArtistMerchIdForFormIO(artistId):
    artist = GlobalState().artists[artistId]

    payload = [{
        "label": f"{v.merchId}",
        "value": f"{v.merchId}",
        "imageLink": v.imageLink,
        "embedCode": generateImageImgComponent(v)
    } for v in filter(
        lambda a: a.currentStock > 0,
        artist.merchMap.values()
    )]

    return payload

def getMerchPrice(artistId, merchId):
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
    return payload

def getListOfAllowedMerchQty(artistId, merchId):
    artist = GlobalState().artists[artistId]
    merch = artist.merchMap[merchId]
    payload = [
        {
            "label": f"{i}",
            "value": i
        }
    for i in range(1, merch.currentStock+1)]
    return payload


"""
Submits the batch of merch orders, and updates a local transaction json.
"""
def updateMerchTransactions(
    requestBodyTransactions
):
    listOfTransactions = map(
        lambda t: Transaction(
            t["artistId"]["value"],
            GlobalState().artists[t["artistId"]["value"]].merchMap[t["merchId"]["value"]],
            t["qty"]["value"],
            t["price"]["value"],
            t
        ),
        requestBodyTransactions
    )

    listOfArtistIds = set(list(map(
        lambda t: t["artistId"]["value"],
        requestBodyTransactions
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

    return True

