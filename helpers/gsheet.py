from commons.constants import OFFSET_MERCH_COL, OFFSET_TRANSACTION_PARTITION_ROW, OFFSET_TRANSACTION_ROW
from oauth2client.service_account import ServiceAccountCredentials
import gspread
import pandas as pd

PATH_TO_CREDENTIALS = "./cred/gsheets/credentials_excel.json"

scope = ['https://spreadsheets.google.com/feeds']
credentials = ServiceAccountCredentials.from_json_keyfile_name(PATH_TO_CREDENTIALS, scope)
df_list = []
client = gspread.authorize(credentials)

def getDfFromWorksheet(worksheet) -> pd.DataFrame:
    worksheet_values = worksheet.get_all_values()
    df_worksheet = pd.DataFrame(worksheet_values)
    # print(df_worksheet)
    df_worksheet.columns = df_worksheet.iloc[2]
    df_worksheet.reset_index(drop=True)
    # print(df_worksheet.iloc[:, 0])

    # indices = df_worksheet.iloc[:, 0] 
    # indices.add(pd.Series(list(range(df_worksheet.shape[0] - OFFSET_TRANSACTION_ROW))))
    # print(indices)
    df_worksheet.index = df_worksheet.iloc[:, 0]
    # df_worksheet.index = [*df_worksheet.iloc[:, 0], *list(range(df_worksheet.shape[0] - OFFSET_TRANSACTION_ROW))]
    df_worksheet = df_worksheet.iloc[:,1:]
    # print(df_worksheet.columns)
    # print(df_worksheet)

    return df_worksheet


"""
Get a Dataframe of all spreadsheets in the worksheet, concatanated one against the next.
"""
def getWorksheetsFromGsheetId(docid, sheetName=None):
    
    spreadsheet = client.open_by_key(docid)
    missing_column_names = None
    output_df = None
    if sheetName:
        worksheets = [
            spreadsheet.worksheet('List of contents'),
            spreadsheet.worksheet('Programming Sheet'),
            spreadsheet.worksheet('Summary'),
            spreadsheet.worksheet(sheetName)
        ]
    else:
        worksheets = spreadsheet.worksheets()
    return worksheets
"""
def getAllWorksheets(docid):
    worksheets = getWorksheetsFromGsheetId(docid)

    # Combine all sheets to one single dataframe.
    for id, worksheet in enumerate(worksheets, start = 1):
        print(worksheet.title)

        worksheet_values = worksheet.get_all_values()

        df_worksheet = pd.DataFrame(worksheet_values)
        print(df_worksheet.shape)
        df_worksheet.columns = df_worksheet.iloc[2]
        df_worksheet.reset_index(drop=True)
        print(df_worksheet.iloc[:, 0])

        # indices = df_worksheet.iloc[:, 0] 
        # indices.add(pd.Series(list(range(df_worksheet.shape[0] - OFFSET_TRANSACTION_ROW))))
        # print(indices)
        df_worksheet.index = df_worksheet.iloc[:, 0]
        # df_worksheet.index = [*df_worksheet.iloc[:, 0], *list(range(df_worksheet.shape[0] - OFFSET_TRANSACTION_ROW))]
        df_worksheet = df_worksheet.iloc[:,1:]

        print(df_worksheet)
        print(df_worksheet.columns)
        print(df_worksheet.loc["Proft", "B1"])
        merchId = 1
        price = 6
        # Get all populated values
        transactions = worksheet.col_values(OFFSET_MERCH_COL + merchId)[OFFSET_TRANSACTION_ROW:]

        merchTransacted = [
            (1, 6),
            (1, 6),
            (1, 6)
        ]
        for id, merch in enumerate(merchTransacted):
            worksheet.update_cell(
                OFFSET_TRANSACTION_ROW + len(transactions) + OFFSET_TRANSACTION_PARTITION_ROW + id, 
                OFFSET_MERCH_COL + merch[0], 
                merch[1]
            ) 

        print(worksheet.col_values(OFFSET_MERCH_COL + merchId)[OFFSET_TRANSACTION_ROW:])

        # Set column to first row, which is the header row in gsheet
        # df_worksheet.columns = df_worksheet.iloc[0]
        # Remove the header row since it is not data.
        # df_worksheet = df_worksheet.iloc[1:,:]

        # df_list.append(df_worksheet) 
        # print(df_worksheet)

    # output_df = pd.concat(df_list)

    return output_df
    """

