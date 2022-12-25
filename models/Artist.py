from typing import List, Tuple
import re
import json

from commons.constants import OFFSET_MERCH_COL, OFFSET_TRANSACTION_PARTITION_ROW, OFFSET_TRANSACTION_ROW
from helpers.gsheet import getDfFromWorksheet

class JSONSerializable():
    def toJSON(self):
        return json.loads(json.dumps(self, default=lambda o: o.__dict__))

class Transaction(JSONSerializable):
    def __init__(self, artistId, merch, qty, price, formRepr):
        self.artistId = artistId
        self.merch = merch
        self.qty = qty
        self.price = price
        self.formRepr = formRepr

class Merch(JSONSerializable):
    def __init__(self, merchId, index, artistId, currentStock, initialPrice, imageLink, discountable = False):
        # print(merchId, index, artistId, currentStock, initialPrice)
        self.artistId = artistId
        self.merchId = merchId
        self.index = index
        self.currentStock = int(currentStock)
        self.initialPrice = initialPrice
        self.imageLink = imageLink
        self.discountable = discountable

class Artist(JSONSerializable):
    def __init__(self, artistName, artistId, worksheet, imageLinks):
        # print(artistName, artistId, worksheet)
        self.artistName = artistName
        self.artistId = artistId
        self.merchMap = {}
        self.imageLinks = imageLinks

    def toJSON(self):
        return {
            "artistName": self.artistName,
            "artistId": self.artistId,
            "merchMap": {i: self.merchMap[i].toJSON() for i in self.merchMap.keys()}
        }

    def updateWorksheet(self, worksheet, discountableMerch):
        self.worksheet = worksheet
        self.df = getDfFromWorksheet(worksheet)
        for i, merch in enumerate(self.df.columns[1:]):
            # print(self.merchMap)
            self.merchMap[merch] = Merch(
                merch,
                i,
                self.artistId,
                self.df.loc['Current Stock', merch],
                self.df.loc['Initial Price', merch],
                self.imageLinks[i],
                merch in discountableMerch
            )

    def handlePurchase(self, transactions: List[Transaction], savedTransactions):
        for id, transaction in enumerate(transactions):
            # print("hi: ", transaction.toJSON())
            existingTransactions = self.worksheet.col_values(OFFSET_MERCH_COL + transaction.merch.index)[OFFSET_TRANSACTION_ROW:]
            
            for i in range(transaction.qty):
                self.worksheet.update_cell(
                    OFFSET_TRANSACTION_ROW + len(existingTransactions) + OFFSET_TRANSACTION_PARTITION_ROW + i, 
                    OFFSET_MERCH_COL + transaction.merch.index, 
                    transaction.price
                ) 

            # print(self.worksheet.col_values(OFFSET_MERCH_COL + transaction.merch.index)[OFFSET_TRANSACTION_ROW:])

            savedTransactions.append(
                transaction.formRepr
            )

    
