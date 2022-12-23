from api.user.models.user import User
from commons.GlobalState import GlobalState
from commons.constants import EOY_TRANSACTION_GSHEET_API_URL, OFFSET_SUMMARY_NAME_ROW
from config.db import db
from flask import Blueprint, jsonify, request
from flask_api import status

from helpers.gsheet import getWorksheetsFromGsheetId
import string

from models.Artist import Artist

import re

artistIdDict = {
    **{c: ord(c) - ord('A') + 1 for c in string.ascii_uppercase},
    'AA': ord('Z') + 2,
    'AB': ord('Z') + 3,
    'AC': ord('Z') + 4,
    'AD': ord('Z') + 5,
}

def update_artists_info(sheet_name):
    print(sheet_name)
    # if len(GlobalState().artists) == 0:
        # sheet_name = None
    worksheets = getWorksheetsFromGsheetId(EOY_TRANSACTION_GSHEET_API_URL)
    locWorksheet = list(filter(lambda ws: ws.title == 'List of contents', worksheets))[0]
    progWorksheet = list(filter(lambda ws: ws.title == 'Programming Sheet', worksheets))[0]
    summaryWorksheet = list(filter(lambda ws: ws.title == 'Summary', worksheets))[0]

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
                print("NAME: ", summaryWorksheet.cell(1, artistCount + OFFSET_SUMMARY_NAME_ROW).value)
                artist = \
                    Artist(
                        summaryWorksheet.cell(1, artistCount + OFFSET_SUMMARY_NAME_ROW).value,
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


def create_user(
    username: str, firstname: str, lastname: str, email:str, address:str, password: str, UserID: str
) -> User:
    user = User(
        username=username,
        firstname=firstname,
        lastname=lastname,
        password=password,
        email=email,
        address=address,
        UserID=UserID,
    )
    db.session.add(user)
    db.session.commit()
    return user

# def read_one_user(
#     **kwargs
# ) -> User:
#     return User.query.filter_by(
#         **kwargs
#     ).all()

def read_one_user(userID):
    res =  User.query.filter_by(userID=userID).first()
    return res


def read_all_user(
    **kwargs
) -> User:
    user = User.query.filter(
        **kwargs
    ).all()

    print(user)

    res = list(map(
        lambda u: u.serialize(),
        user
    ))

    print("res", res)
    db.session.commit()

    return( jsonify(
        success=True,
        data=res
    ), status.HTTP_200_OK)

def update_users(

   username: str, firstName: str, lastName: str, email: str, address: str, userID: str
) -> User:
    user = User.query.filter_by(userID = userID)

    user.update({
        "username":username ,
        "firstName":firstName,
        "lastName":lastName,
        "email":email,
        "address":address,
        })

    res = list(map(
            lambda u: u.serialize(),
            user
        ))

    db.session.commit()


    return res

def update_user_password(

    userID: str , username: str, password: str
) -> User:
    user = User.query.filter_by(userID = userID)

    user.update({"password":password})

    res = list(map(
        lambda u: u.serialize(),
        user
    ))

    db.session.commit()

    return res

