from typing import List, Tuple
import re
import json

from commons.constants import OFFSET_MERCH_COL, OFFSET_TRANSACTION_PARTITION_ROW, OFFSET_TRANSACTION_ROW
from helpers.gsheet import getDfFromWorksheet

class JSONSerializable():
    def toJSON(self):
        return json.loads(json.dumps(self, default=lambda o: o.__dict__))

class Transaction(JSONSerializable):
    def __init__(self, artistId, merchId, qty, price):
        self.artistId = artistId
        self.merchId = merchId
        self.qty = qty
        self.price = price

class Merch(JSONSerializable):
    def __init__(self, merchId, artistId, currentStock, initialPrice, discountable = False):
        print(merchId, artistId, currentStock, initialPrice)
        self.artistId = artistId
        self.merchId = merchId
        self.currentStock = currentStock
        self.initialPrice = initialPrice
        self.discountable = discountable

class Artist(JSONSerializable):
    def __init__(self, artistName, artistId, worksheet):
        print(artistName, artistId, worksheet)
        self.artistName = artistName
        self.artistId = artistId
        self.merchMap = {}

    def toJSON(self):
        return {
            "artistName": self.artistName,
            "artistId": self.artistId,
            "merchMap": {i: self.merchMap[i].toJSON() for i in self.merchMap.keys()}
        }

    def updateWorksheet(self, worksheet, discountableMerch):
        self.worksheet = worksheet
        self.df = getDfFromWorksheet(worksheet)

        for merch in filter(
            lambda x: re.match(r'[A-Z]+[0-9]+', x),
            self.df.columns
        ):
            print("MERCH: ", merch)

            print(self.merchMap)
            self.merchMap[merch] = Merch(
                re.search(r'[0-9]+', merch).group(),
                self.artistId,
                self.df.loc['Current Stock', merch],
                self.df.loc['Initial Price', merch],
                merch in discountableMerch
            )

    def handlePurchase(self, transactions: List[Transaction]):
        for id, transaction in enumerate(transactions):
            print("hi: ", transaction.toJSON())
            existingTransactions = self.worksheet.col_values(OFFSET_MERCH_COL + transaction.merchId)[OFFSET_TRANSACTION_ROW:]
            
            for i in range(transaction.qty):
                self.worksheet.update_cell(
                    OFFSET_TRANSACTION_ROW + len(existingTransactions) + OFFSET_TRANSACTION_PARTITION_ROW + i, 
                    OFFSET_MERCH_COL + transaction.merchId, 
                    transaction.price
                ) 

            print(self.worksheet.col_values(OFFSET_MERCH_COL + transaction.merchId)[OFFSET_TRANSACTION_ROW:])

    
