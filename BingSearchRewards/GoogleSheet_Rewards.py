#from __future__ import print_function

import os

import BingSearchRewards.common
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials


class GoogleSheet_Rewards:
    def __init__(self):
        # If modifying these scopes, delete the file token.json.
        self.SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

        # The ID and range of a sample spreadsheet.
        self.SPREADSHEET_ID = '1BH-LiKTC8zGfWWq5wq3KfYGj8pd7Bj2MjvRmf5q1wM4'
        ##self.RANGE_NAME = 'RewardsData!A2:E'

    def updatesheet(self, userid, points, tag):
        """Shows basic usage of the Sheets API.
        Prints values from a sample spreadsheet.
        """
        credentials = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.json'):
            credentials = Credentials.from_authorized_user_file('token.json', self.SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
            else:
                if not os.path.exists('credentials.json'):
                    create_file('credentials.json', '{ "installed": { "auth_uri": "", "token_uri": "", "client_id": "" } }')
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', self.SCOPES)
                credentials = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(credentials.to_json())

        service = build('sheets', 'v4', credentials=credentials)

        # Call the Sheets API
        RANGE_NAME = "{0}!A2:E".format(userid.split('@')[0])
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=self.SPREADSHEET_ID,
                                    range=RANGE_NAME).execute()
        values = result.get('values', [])

        if not values:
            print('No data found.')
        else:
            print('Name, Major:')
            for row in values:
                # Print columns A and E, which correspond to indices 0 and 4.
                print('%s, %s' % (row[0], row[4]))



if __name__ == '__main__':
    sheet = GoogleSheet_Rewards()
    sheet.updatesheet("ted_250@hotmail.com", 100_000, "test")